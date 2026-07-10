import React, { useState, useEffect } from 'react';
import { listCustomFields, deleteCustomField, getApiErrorMessage } from '../services/api';

const TYPE_LABELS = {
  text: 'Text',
  number: 'Number',
  alphanumeric: 'Letters & Digits',
  date: 'Date',
  datetime: 'Date & Time',
};

export default function CustomFieldList({ onFieldDeleted }) {
  const [fields, setFields] = useState([]);
  const [error, setError] = useState(null);
  const [deleteError, setDeleteError] = useState(null);

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
    setDeleteError(null);
    try {
      await deleteCustomField(id);
      setFields(prev => prev.filter(field => field.id !== id));
      onFieldDeleted(id);
    } catch (error) {
      console.error('Error deleting custom field:', error);
      setDeleteError(getApiErrorMessage(error, 'The field could not be deleted. Please try again.'));
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
      {deleteError && (
        <div role="alert" className="rounded-lg bg-red-900/40 border border-red-700 text-red-200 text-sm px-4 py-3">
          {deleteError}
        </div>
      )}
      {fields.map(field => (
        <div key={field.id} className="bg-gray-700 rounded-lg p-4">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-medium text-white">{field.name}</h3>
              <p className="text-sm text-gray-400">Type: {TYPE_LABELS[field.field_type] || field.field_type}</p>
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