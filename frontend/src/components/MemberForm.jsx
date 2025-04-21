import React, { useState } from 'react';
import { generateMembers } from '../services/api';

export default function MemberForm({ onData }) {
  const [city, setCity] = useState('Copenhagen');
  const [country, setCountry] = useState('Denmark');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = await generateMembers({ city, country });
    onData(data);
  };

  return (
    <form onSubmit={handleSubmit} className="p-4">
      <input type="text" value={city} onChange={(e) => setCity(e.target.value)} />
      <input type="text" value={country} onChange={(e) => setCountry(e.target.value)} />
      <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">Generate</button>
    </form>
  );
}