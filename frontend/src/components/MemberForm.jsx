import React, { useState } from 'react';
import { generateMembers, getApiErrorMessage } from '../services/api';

const inputClass = "block w-full rounded-lg border-gray-600 bg-gray-700 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm";

export default function MemberForm({ onGenerate }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
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

    if (config.min_age > config.max_age) {
      setError('The first age must be lower than the second age.');
      return;
    }

    setError(null);
    setIsLoading(true);
    try {
      const members = await generateMembers(config);
      onGenerate(members);
    } catch (err) {
      console.error('Error generating members:', err);
      setError(getApiErrorMessage(err, 'Something went wrong while generating members. Please try again.'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-6 space-y-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div className="space-y-2">
          <label htmlFor="generate-city" className="block text-sm font-medium text-gray-300">City</label>
          <input
            id="generate-city"
            type="text"
            name="city"
            value={config.city}
            onChange={handleChange}
            className={inputClass}
            required
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="generate-country" className="block text-sm font-medium text-gray-300">Country</label>
          <input
            id="generate-country"
            type="text"
            name="country"
            value={config.country}
            onChange={handleChange}
            className={inputClass}
            required
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="generate-count" className="block text-sm font-medium text-gray-300">Number of Members</label>
          <input
            id="generate-count"
            type="number"
            name="count"
            value={config.count}
            onChange={handleChange}
            min="1"
            max="100"
            className={inputClass}
            required
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="generate-min-age" className="block text-sm font-medium text-gray-300">Age Range</label>
          <div className="flex items-center gap-2">
            <input
              id="generate-min-age"
              type="number"
              name="min_age"
              aria-label="Minimum age"
              value={config.min_age}
              onChange={handleChange}
              min="0"
              max="120"
              className={inputClass}
              required
            />
            <span className="text-gray-400">to</span>
            <input
              id="generate-max-age"
              type="number"
              name="max_age"
              aria-label="Maximum age"
              value={config.max_age}
              onChange={handleChange}
              min="0"
              max="120"
              className={inputClass}
              required
            />
          </div>
        </div>
      </div>
      {error && (
        <div role="alert" className="rounded-lg bg-red-900/40 border border-red-700 text-red-200 text-sm px-4 py-3">
          {error}
        </div>
      )}
      <button
        type="submit"
        disabled={isLoading}
        className={`w-full py-2 px-4 rounded-lg text-sm font-medium text-white transition-colors ${
          isLoading
            ? 'bg-blue-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-blue-500'
        }`}
      >
        {isLoading ? 'Generating Members... (this can take a while)' : 'Generate Members'}
      </button>
    </form>
  );
}
