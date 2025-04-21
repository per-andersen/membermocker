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
    <form onSubmit={handleSubmit} className="p-6 space-y-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">City</label>
          <input
            type="text"
            name="city"
            value={config.city}
            onChange={handleChange}
            className="block w-full rounded-lg border-gray-600 bg-gray-700 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            required
          />
        </div>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">Country</label>
          <input
            type="text"
            name="country"
            value={config.country}
            onChange={handleChange}
            className="block w-full rounded-lg border-gray-600 bg-gray-700 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            required
          />
        </div>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">Number of Members</label>
          <input
            type="number"
            name="count"
            value={config.count}
            onChange={handleChange}
            min="1"
            max="100"
            className="block w-full rounded-lg border-gray-600 bg-gray-700 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            required
          />
        </div>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">Age Range</label>
          <div className="flex items-center gap-2">
            <input
              type="number"
              name="min_age"
              value={config.min_age}
              onChange={handleChange}
              min="0"
              max="120"
              className="block w-full rounded-lg border-gray-600 bg-gray-700 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              required
            />
            <span className="text-gray-400">to</span>
            <input
              type="number"
              name="max_age"
              value={config.max_age}
              onChange={handleChange}
              min="0"
              max="120"
              className="block w-full rounded-lg border-gray-600 bg-gray-700 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              required
            />
          </div>
        </div>
      </div>
      <button
        type="submit"
        className="w-full py-2 px-4 rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-blue-500 transition-colors"
      >
        Generate Members
      </button>
    </form>
  );
}