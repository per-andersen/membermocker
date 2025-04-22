import React, { useEffect, useRef } from 'react';

export default function MapView({ members }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    // Load OpenStreetMap script and styles if not already loaded
    if (!window.L) {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/leaflet/dist/leaflet.js';
      script.async = true;

      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet/dist/leaflet.css';

      document.head.appendChild(link);
      document.body.appendChild(script);

      script.onload = initializeMap;
    } else {
      initializeMap();
    }

    function initializeMap() {
      if (!mapRef.current) return;
      
      // Cleanup previous map instance if it exists
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
      }

      const L = window.L;
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
            const marker = L.marker([member.latitude, member.longitude])
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
        if (!bounds.isEmpty()) {
          map.fitBounds(bounds);
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