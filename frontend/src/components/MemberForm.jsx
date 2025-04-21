import React, { useState } from 'react';
import { generateMembers } from '../services/api';

export default function MemberForm({ onGenerate }) {
  const [config, setConfig] = useState({
    city: 'Copenhagen',
    country: 'Denmark',
    count: 1,
    min_age: 18,
    max_age: 90
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: name === 'count' || name === 'min_age' || name === 'max_age' 
        ? parseInt(value, 10) 
        : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const members = await generateMembers(config);
      onGenerate(members);
    } catch (error) {
      console.error('Error generating members:', error);
      alert('Failed to generate members. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-white rounded shadow">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">City</label>
          <input
            type="text"
            name="city"
            value={config.city}
            onChange={handleChange}
            className="mt-1 block w-full rounded border-gray-300 shadow-sm"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Country</label>
          <input
            type="text"
            name="country"
            value={config.country}
            onChange={handleChange}
            className="mt-1 block w-full rounded border-gray-300 shadow-sm"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Number of Members</label>
          <input
            type="number"
            name="count"
            value={config.count}
            onChange={handleChange}
            min="1"
            max="100"
            className="mt-1 block w-full rounded border-gray-300 shadow-sm"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Age Range</label>
          <div className="flex gap-2">
            <input
              type="number"
              name="min_age"
              value={config.min_age}
              onChange={handleChange}
              min="0"
              max="120"
              className="mt-1 block w-full rounded border-gray-300 shadow-sm"
              required
            />
            <span className="mt-1">to</span>
            <input
              type="number"
              name="max_age"
              value={config.max_age}
              onChange={handleChange}
              min="0"
              max="120"
              className="mt-1 block w-full rounded border-gray-300 shadow-sm"
              required
            />
          </div>
        </div>
      </div>
      <button
        type="submit"
        className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
      >
        Generate Members
      </button>
    </form>
  );
}