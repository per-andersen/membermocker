import React, { useState, useEffect } from 'react';
import { listCustomFields, deleteCustomField } from '../services/api';

export default function CustomFieldList({ onFieldDeleted }) {
  const [fields, setFields] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadFields();
  }, []);

  const loadFields = async () => {
    try {
      const data = await listCustomFields();
      setFields(data);
      setError(null);
    } catch (error) {
      console.error('Error loading custom fields:', error);
      setError('Failed to load custom fields. Please try again.');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this custom field? All values for this field will be deleted.')) {
      return;
    }
    try {
      await deleteCustomField(id);
      setFields(prev => prev.filter(field => field.id !== id));
      onFieldDeleted(id);
    } catch (error) {
      console.error('Error deleting custom field:', error);
      alert('Failed to delete custom field. Please try again.');
    }
  };

  if (error) {
    return <div className="text-red-400 px-6 py-4">{error}</div>;
  }

  if (!fields.length) {
    return <p className="text-gray-400 text-center py-4">No custom fields defined yet.</p>;
  }

  return (
    <div className="space-y-4">
      {fields.map(field => (
        <div key={field.id} className="bg-gray-700 rounded-lg p-4">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-medium text-white">{field.name}</h3>
              <p className="text-sm text-gray-400">Type: {field.field_type}</p>
              {Object.entries(field.validation_rules).length > 0 && (
                <div className="mt-2">
                  <p className="text-sm text-gray-400">Validation Rules:</p>
                  <ul className="list-disc list-inside text-sm text-gray-400">
                    {Object.entries(field.validation_rules).map(([rule, value]) => (
                      <li key={rule}>
                        {rule.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}: {value}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            <button
              onClick={() => handleDelete(field.id)}
              className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-sm"
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}