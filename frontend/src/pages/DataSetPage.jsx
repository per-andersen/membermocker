import React, { useState, useEffect } from 'react';
import MemberForm from '../components/MemberForm';
import MemberList from '../components/MemberList';
import CustomFieldForm from '../components/CustomFieldForm';
import CustomFieldList from '../components/CustomFieldList';
import { listMembers } from '../services/api';

export default function DataSetPage() {
  const [members, setMembers] = useState([]);
  const [error, setError] = useState(null);
  const [showCustomFields, setShowCustomFields] = useState(false);

  useEffect(() => {
    loadMembers();
  }, []);

  const loadMembers = async () => {
    try {
      const data = await listMembers();
      setMembers(data);
      setError(null);
    } catch (error) {
      console.error('Error loading members:', error);
      if (error.response?.status !== 404) {
        setError('Failed to load members. Please try again.');
      }
    }
  };

  const handleGenerate = (newMembers) => {
    setMembers(prev => [...prev, ...newMembers]);
  };

  const handleMemberDeleted = (deletedId) => {
    setMembers(prev => prev.filter(m => m.id !== deletedId));
  };

  const handleMemberUpdated = (updatedMember) => {
    setMembers(prev => prev.map(m => 
      m.id === updatedMember.id ? updatedMember : m
    ));
  };

  const handleCustomFieldCreated = () => {
    // Reload all members to get updated custom field values
    loadMembers();
  };

  const handleCustomFieldDeleted = () => {
    // Reload all members to get updated custom field values
    loadMembers();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <section className="rounded-xl overflow-hidden bg-gray-800 shadow-lg">
        <h2 className="text-xl font-bold p-6 border-b border-gray-700">Generate New Members</h2>
        <MemberForm onGenerate={handleGenerate} />
      </section>
      
      <section className="rounded-xl overflow-hidden bg-gray-800 shadow-lg">
        <div className="flex justify-between items-center p-6 border-b border-gray-700">
          <h2 className="text-xl font-bold">Member List</h2>
          <button
            onClick={() => setShowCustomFields(!showCustomFields)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            {showCustomFields ? 'Hide Custom Fields' : 'Manage Custom Fields'}
          </button>
        </div>
        
        {showCustomFields && (
          <div className="p-6 border-b border-gray-700 bg-gray-850">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-4">Add Custom Field</h3>
                <CustomFieldForm onFieldCreated={handleCustomFieldCreated} />
              </div>
              <div>
                <h3 className="text-lg font-medium mb-4">Custom Fields</h3>
                <CustomFieldList onFieldDeleted={handleCustomFieldDeleted} />
              </div>
            </div>
          </div>
        )}

        {error && <div className="text-red-400 px-6 py-4">{error}</div>}
        <MemberList 
          members={members}
          onMemberDeleted={handleMemberDeleted}
          onMemberUpdated={handleMemberUpdated}
        />
      </section>
    </div>
  );
}