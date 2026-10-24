import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Leaflet guesses its icon URLs from the CSS path, which breaks once bundled
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

export default function MapView({ members }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    initializeMap();

    function initializeMap() {
      if (!mapRef.current) return;
      
      // Cleanup previous map instance if it exists
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
      }

      // Initialize map with default view
      const map = L.map(mapRef.current).setView([0, 0], 2);
      mapInstanceRef.current = map;

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(map);

      if (members?.length) {
        // Add markers for each member
        const bounds = L.latLngBounds();
        members.forEach(member => {
          if (member.latitude && member.longitude) {
            L.marker([member.latitude, member.longitude])
              .bindPopup(`
                <b>${member.first_name} ${member.surname}</b><br>
                ${member.address}<br>
                ${member.email}<br>
                ${member.phone_number}
              `)
              .addTo(map);
            bounds.extend([member.latitude, member.longitude]);
          }
        });

        // Fit map to show all markers
        if (bounds.isValid()) {
          map.fitBounds(bounds, { maxZoom: 15, padding: [30, 30] });
        }
      }
    }

    // Cleanup function
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [members]);

  return (
    <div 
      ref={mapRef} 
      className="w-full h-[600px] rounded-lg overflow-hidden"
      style={{ background: '#f8f9fa' }}
    />
  );
}