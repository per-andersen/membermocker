import React, { useState } from 'react';
import { createCustomField } from '../services/api';

export default function CustomFieldForm({ onFieldCreated }) {
  const [isLoading, setIsLoading] = useState(false);
  const [field, setField] = useState({
    name: '',
    field_type: 'string',
    validation_rules: {}
  });

  const fieldTypes = [
    { value: 'string', label: 'Text', rules: ['min_length', 'max_length'] },
    { value: 'integer', label: 'Number', rules: ['min', 'max', 'digits'] },
    { value: 'alphanumeric', label: 'Alphanumeric', rules: ['length'] },
    { value: 'email', label: 'Email', rules: [] },
    { value: 'phone', label: 'Phone Number', rules: ['format'] },
    { value: 'date', label: 'Date', rules: ['min_date', 'max_date'] }
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setField(prev => ({
      ...prev,
      [name]: value,
      validation_rules: name === 'field_type' ? {} : prev.validation_rules
    }));
  };

  const handleRuleChange = (e) => {
    const { name, value } = e.target;
    setField(prev => ({
      ...prev,
      validation_rules: {
        ...prev.validation_rules,
        [name]: value
      }
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const newField = await createCustomField(field);
      onFieldCreated(newField);
      setField({
        name: '',
        field_type: 'string',
        validation_rules: {}
      });
    } catch (error) {
      console.error('Error creating custom field:', error);
      alert('Failed to create custom field. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getValidationFields = () => {
    const selectedType = fieldTypes.find(type => type.value === field.field_type);
    if (!selectedType) return null;

    return selectedType.rules.map(rule => (
      <div key={rule} className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">
          {rule.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
        </label>
        <input
          type={rule.includes('length') || rule.includes('digits') ? 'number' : 'text'}
          name={rule}
          value={field.validation_rules[rule] || ''}
          onChange={handleRuleChange}
          className="block w-full rounded-lg border-gray-600 bg-gray-700 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>
    ));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">Field Name</label>
          <input
            type="text"
            name="name"
            value={field.name}
            onChange={handleChange}
            className="block w-full rounded-lg border-gray-600 bg-gray-700 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            required
          />
        </div>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">Field Type</label>
          <select
            name="field_type"
            value={field.field_type}
            onChange={handleChange}
            className="block w-full rounded-lg border-gray-600 bg-gray-700 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            {fieldTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-medium text-gray-300">Validation Rules</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {getValidationFields()}
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className={`w-full py-2 px-4 rounded-lg text-sm font-medium text-white transition-colors ${
          isLoading 
            ? 'bg-blue-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-blue-500'
        }`}
      >
        {isLoading ? 'Creating Field...' : 'Create Custom Field'}
      </button>
    </form>
  );
}