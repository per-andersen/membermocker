import React, { useState, useEffect } from 'react';
import MemberForm from '../components/MemberForm';
import MemberList from '../components/MemberList';
import { listMembers } from '../services/api';

export default function DataSetPage() {
  const [members, setMembers] = useState([]);

  useEffect(() => {
    loadMembers();
  }, []);

  const loadMembers = async () => {
    try {
      const data = await listMembers();
      setMembers(data);
    } catch (error) {
      console.error('Error loading members:', error);
      alert('Failed to load members. Please try again.');
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

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-8">
      <section>
        <h2 className="text-xl font-bold mb-4">Generate New Members</h2>
        <MemberForm onGenerate={handleGenerate} />
      </section>
      
      <section>
        <h2 className="text-xl font-bold mb-4">Member List</h2>
        <MemberList 
          members={members}
          onMemberDeleted={handleMemberDeleted}
          onMemberUpdated={handleMemberUpdated}
        />
      </section>
    </div>
  );
}