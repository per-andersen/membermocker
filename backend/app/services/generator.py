import random
import requests
import gzip
import csv
import io
import pycountry
from ollama import chat
from app.models.member import MemberConfig, Member
from app.core.config import get_db
from typing import List, Tuple

def generate_members(config: MemberConfig) -> List[Member]:
    """
    Generates fictitious group members using llama3.1 and ollama.
    Args:
        config (MemberConfig): Configuration for generating members.
    Returns:
        List[Member]: A list of generated members.
    """
    
    addresses_with_coords = get_real_addresses(config.city, config.country, config.count)
    db = get_db()
    
    members = []
    for i in range(config.count):
        response = chat(
            messages=[
                {
                    'role': 'user',
                    'content': f'Get the data for this ficticious group member from the city of {config.city}, {config.country}. Their age should be between {config.min_age} and {config.max_age} years old. Leave the custom fields empty.',
                }
            ],
            model='llama3.1',
            format=Member.model_json_schema(),
        )
        
        member = Member.model_validate_json(response.message.content)
        member.custom_fields = None
        if i < len(addresses_with_coords):
            address, lat, lon = addresses_with_coords[i]
            member.address = address
            member.latitude = lat
            member.longitude = lon
            
        # Insert the member
        db.execute("""
            INSERT INTO members 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            str(member.id),
            member.date_member_joined_group,
            member.first_name,
            member.surname,
            member.birthday,
            member.phone_number,
            member.email,
            member.address,
            member.latitude,
            member.longitude
        ])
        
        members.append(member)
    
    return members

def _get_country_code(country_name: str) -> str:
    """
    Maps country names to ISO 3166-1 alpha-2 country codes using fuzzy search.
    Args:
        country_name (str): The country name (e.g., "Danmark", "Italia", "Denmark")
    Returns:
        str: The ISO 3166-1 alpha-2 country code (e.g., "DK", "IT")
    """
    matches = pycountry.countries.search_fuzzy(country_name)
    if matches:
        return matches[0].alpha_2
    raise Exception(f"Could not determine country code for: {country_name}")

def _fetch_country_addresses(country_code: str) -> List[dict]:
    """
    Fetches and parses address data from openstreetdata.org for a country.
    Args:
        country_code (str): ISO 3166-1 alpha-2 country code (e.g., "DK", "IT")
    Returns:
        List[dict]: List of address records with columns as dictionary keys
    """
    url = f"https://files.openstreetdata.org/addresses/{country_code.upper()}-addresses.tsv.gz"
    
    headers = {
        'User-Agent': 'MemberMocker/1.0 (membermocker@proton.me)'
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz:
        text_content = gz.read().decode('utf-8')
    
    records = []
    reader = csv.DictReader(io.StringIO(text_content), delimiter='\t')
    for row in reader:
        records.append(row)
    
    return records

def get_real_addresses(city: str, country: str, count: int) -> List[Tuple[str, float, float]]:
    """
    Fetches real addresses with coordinates from OpenStreetMap data via openstreetdata.org.
    Uses street data and generates valid house numbers within the city's bounding box.
    
    Args:
        city (str): The city to search for.
        country (str): The country to search in.
        count (int): The number of addresses to fetch.
    Returns:
        List[Tuple[str, float, float]]: A list of tuples containing (address, latitude, longitude).
    """
    headers = {
        'User-Agent': 'MemberMocker/1.0 (membermocker@proton.me)'
    }

    # Step 1: Get the city's bounding box using Nominatim
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'city': city,
        'country': country,
        'format': 'json',
        'limit': 1,
        'addressdetails': 1,
    }

    response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    results = response.json()
    
    if not results:
        raise ValueError(f"City not found: {city}, {country}")

    city_data = results[0]
    bbox = city_data.get('boundingbox')
    if not bbox:
        raise ValueError(f"No bounding box found for {city}, {country}")
    
    south, north, west, east = map(float, bbox)
    
    target_municipality = city_data.get('address', {}).get('municipality', city).strip()

    # Step 2: Get country code and fetch address data
    country_code = _get_country_code(country)
    address_records = _fetch_country_addresses(country_code)
    
    # Step 3: Filter streets within the city's bounding box and from the target municipality
    filtered_streets = []
    for record in address_records:
        try:
            record_city = record.get('city_').strip()
            
            if record_city != target_municipality:
                continue
            
            x_min = float(record.get('x_min'))
            x_max = float(record.get('x_max'))
            y_min = float(record.get('y_min'))
            y_max = float(record.get('y_max'))
            
            if x_min <= east and x_max >= west and y_min <= north and y_max >= south:
                record_street = record.get('street_').strip()
                record_postal = record.get('postal_code_').strip()
                
                house_min = int(record.get('house_min'))
                house_max = int(record.get('house_max'))
                
                if house_max >= house_min and record_street:
                    filtered_streets.append({
                        'street': record_street,
                        'city': record_city,
                        'postal_code': record_postal,
                        'house_min': house_min,
                        'house_max': house_max,
                        'x_min': x_min,
                        'x_max': x_max,
                        'y_min': y_min,
                        'y_max': y_max,
                    })
        except (ValueError, KeyError):
            continue
    
    if not filtered_streets:
        raise Exception(f"No streets found in {city}, {country} within bounding box")

    # Step 4: Generate addresses by randomly selecting streets and house numbers
    address_data = []
    attempts = 0
    max_attempts = count * 10
    
    while len(address_data) < count and attempts < max_attempts:
        street_record = random.choice(filtered_streets)
        
        house_num = random.randint(street_record['house_min'], street_record['house_max'])
        
        lat = random.uniform(street_record['y_min'], street_record['y_max'])
        lon = random.uniform(street_record['x_min'], street_record['x_max'])
        
        full_address = f"{street_record['street']} {house_num}, {street_record['postal_code']}, {street_record['city']}, {country}"
        
        if (full_address, lat, lon) not in address_data:
            address_data.append((full_address, lat, lon))
        
        attempts += 1
    
    if not address_data:
        raise Exception(f"Could not generate any addresses for {city}, {country}")

    return address_data[:count]
