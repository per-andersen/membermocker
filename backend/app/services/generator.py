import random
import requests
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
    
    members = []
    for i in range(config.count):
        response = chat(
            messages=[
                {
                    'role': 'user',
                    'content': f'Get the data for this ficticious group member from the city of {config.city}, {config.country}. Their age should be between {config.min_age} and {config.max_age} years old.',
                }
            ],
            model='llama3.1',
            format=Member.model_json_schema(),
        )
        
        member = Member.model_validate_json(response.message.content)
        if i < len(addresses_with_coords):
            address, lat, lon = addresses_with_coords[i]
            member.address = address
            member.latitude = lat
            member.longitude = lon
        members.append(member)
    
    db = get_db()
    for member in members:
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
    
    return members

def get_real_addresses(city: str, country: str, count: int) -> List[Tuple[str, float, float]]:
    """
    Fetches real addresses with coordinates from OpenStreetMap using Nominatim and Overpass API.
    Args:
        city (str): The city to search for.
        country (str): The country to search in.
        count (int): The number of addresses to fetch.
    Returns:
        List[Tuple[str, float, float]]: A list of tuples containing (address, latitude, longitude).
    """
    headers = {
        'User-Agent': 'RealAddressFetcher/1.0 (realaddressfetcher@example.com)'
    }

    # Step 1: Query Nominatim directly with city and full country name
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'city': city,
        'country': country,
        'format': 'json',
        'limit': 1,
        'addressdetails': 1,
        'extratags': 1
    }

    r = requests.get(nominatim_url, params=params, headers=headers)
    r.raise_for_status()
    results = r.json()
    if not results:
        raise Exception("City not found.")

    city_data = results[0]
    bbox = city_data['boundingbox']  # [south, north, west, east]
    south, north, west, east = bbox

    # Step 2: Get native city name from 'wikipedia' tag
    native_city_name = city  # fallback
    wiki_tag = city_data.get("extratags", {}).get("wikipedia")
    if wiki_tag and ':' in wiki_tag:
        _, native = wiki_tag.split(':', 1)
        native_city_name = native.strip()

    # Step 3: Query Overpass using bounding box
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node["addr:street"]["addr:housenumber"]({south},{west},{north},{east});
    );
    out body;
    """

    response = requests.post(overpass_url, data=overpass_query, headers=headers)
    response.raise_for_status()
    result = response.json()

    nodes = result.get('elements', [])
    random.shuffle(nodes)
    address_data = []

    for node in nodes:
        tags = node.get('tags', {})
        street = tags.get("addr:street")
        housenumber = tags.get("addr:housenumber")
        postcode = tags.get("addr:postcode", "")
        city_candidate = tags.get("addr:city") or tags.get("addr:town") or tags.get("addr:village")

        if street and housenumber:
            if city_candidate and native_city_name.lower() in city_candidate.lower():
                full_address = f"{street} {housenumber}, {postcode}, {city_candidate}, {country}"
                lat = node.get('lat')
                lon = node.get('lon')
                if lat is not None and lon is not None:
                    address_data.append((full_address, float(lat), float(lon)))

        if len(address_data) >= count:
            break

    return address_data
