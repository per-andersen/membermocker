import React, { useState } from 'react';
import { updateMember, deleteMember, downloadMembers, getApiErrorMessage } from '../services/api';
import MapView from './MapView';

export default function MemberList({ members, onMemberDeleted, onMemberUpdated }) {
  const [editingMember, setEditingMember] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [editError, setEditError] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [viewMode, setViewMode] = useState('list'); // 'list', 'grid', or 'map'

  const handleEdit = (member) => {
    setEditingMember(member.id);
    setEditError(null);
    setEditForm({
      ...member,
      custom_fields: member.custom_fields || {}
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('custom_')) {
      // Handle custom field changes
      const fieldName = name.replace('custom_', '');
      setEditForm(prev => ({
        ...prev,
        custom_fields: {
          ...prev.custom_fields,
          [fieldName]: value
        }
      }));
    } else {
      // Handle regular field changes
      setEditForm(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleSave = async (id) => {
    setEditError(null);
    setIsSaving(true);
    try {
      const updated = await updateMember(id, editForm);
      setEditingMember(null);
      onMemberUpdated(updated);
    } catch (error) {
      console.error('Error updating member:', error);
      setEditError(getApiErrorMessage(error, 'The changes could not be saved. Please try again.'));
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this member?')) return;
    try {
      await deleteMember(id);
      onMemberDeleted(id);
    } catch (error) {
      console.error('Error deleting member:', error);
      alert('Failed to delete member. Please try again.');
    }
  };

  const handleDownload = async (format) => {
    try {
      await downloadMembers(format);
    } catch (error) {
      console.error('Error downloading members:', error);
      alert('Failed to download members. Please try again.');
    }
  };

  if (!members?.length) {
    return <p className="text-gray-400 text-center py-8">No members generated yet.</p>;
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('list')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              viewMode === 'list'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            List View
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              viewMode === 'grid'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Grid View
          </button>
          <button
            onClick={() => setViewMode('map')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              viewMode === 'map'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Map View
          </button>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => handleDownload('csv')}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm"
          >
            Download CSV
          </button>
          <button
            onClick={() => handleDownload('excel')}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm"
          >
            Download Excel
          </button>
        </div>
      </div>

      {viewMode === 'map' ? (
        <MapView members={members} />
      ) : (
        <div className={`${viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4' : 'grid gap-4'}`}>
          {members.map(member => (
            <div key={member.id} className="p-6 bg-gray-700 rounded-lg shadow-md">
              {editingMember === member.id ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { name: 'first_name', label: 'First Name', type: 'text' },
                      { name: 'surname', label: 'Surname', type: 'text' },
                      { name: 'email', label: 'Email', type: 'email' },
                      { name: 'phone_number', label: 'Phone', type: 'tel' },
                      { name: 'address', label: 'Address', type: 'text', span: true },
                    ].map(({ name, label, type, span }) => (
                      <div key={name} className={span ? 'col-span-2' : ''}>
                        <label htmlFor={`edit-${name}-${member.id}`} className="block text-sm font-medium text-gray-300 mb-1">
                          {label}
                        </label>
                        <input
                          id={`edit-${name}-${member.id}`}
                          type={type}
                          name={name}
                          value={editForm[name]}
                          onChange={handleChange}
                          className="block w-full rounded-lg border-gray-600 bg-gray-800 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        />
                      </div>
                    ))}
                    <div>
                      <label htmlFor={`edit-birthday-${member.id}`} className="block text-sm font-medium text-gray-300 mb-1">
                        Birthday
                      </label>
                      <input
                        id={`edit-birthday-${member.id}`}
                        type="date"
                        name="birthday"
                        value={editForm.birthday}
                        onChange={handleChange}
                        className="block w-full rounded-lg border-gray-600 bg-gray-800 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label htmlFor={`edit-joined-${member.id}`} className="block text-sm font-medium text-gray-300 mb-1">
                        Date Joined
                      </label>
                      <input
                        id={`edit-joined-${member.id}`}
                        type="date"
                        name="date_member_joined_group"
                        value={editForm.date_member_joined_group}
                        onChange={handleChange}
                        className="block w-full rounded-lg border-gray-600 bg-gray-800 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                    {editForm.custom_fields && Object.entries(editForm.custom_fields).map(([fieldName, value]) => (
                      <div key={fieldName} className="col-span-2">
                        <label htmlFor={`edit-custom-${fieldName}-${member.id}`} className="block text-sm font-medium text-gray-300 mb-1">
                          {fieldName}
                        </label>
                        <input
                          id={`edit-custom-${fieldName}-${member.id}`}
                          type="text"
                          name={`custom_${fieldName}`}
                          value={value || ''}
                          onChange={handleChange}
                          className="block w-full rounded-lg border-gray-600 bg-gray-800 text-gray-100 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        />
                      </div>
                    ))}
                  </div>
                  {editError && (
                    <div role="alert" className="rounded-lg bg-red-900/40 border border-red-700 text-red-200 text-sm px-4 py-3">
                      {editError}
                    </div>
                  )}
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => setEditingMember(null)}
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition-colors text-sm"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleSave(member.id)}
                      disabled={isSaving}
                      className={`px-4 py-2 text-white rounded-lg transition-colors text-sm ${
                        isSaving ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                      }`}
                    >
                      {isSaving ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <div className={`flex ${viewMode === 'grid' ? 'flex-col space-y-4' : 'justify-between items-start'}`}>
                    <div className="space-y-2">
                      <h3 className="font-bold text-lg text-white">{member.first_name} {member.surname}</h3>
                      <p className="text-gray-300">{member.email}</p>
                      <p className="text-gray-300">{member.phone_number}</p>
                      <p className="text-gray-300">{member.address}</p>
                      <div className="flex gap-4 text-sm text-gray-400">
                        <p>Born: {new Date(member.birthday).toLocaleDateString()}</p>
                        <p>Joined: {new Date(member.date_member_joined_group).toLocaleDateString()}</p>
                      </div>
                      {member.custom_fields && Object.entries(member.custom_fields).length > 0 && (
                        <div className="border-t border-gray-600 mt-3 pt-3">
                          <h4 className="text-sm font-medium text-gray-400 mb-2">Custom Fields</h4>
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            {Object.entries(member.custom_fields).map(([fieldName, value]) => (
                              <div key={fieldName}>
                                <span className="text-gray-400">{fieldName}:</span>{' '}
                                {value ? (
                                  <span className="text-gray-300">{value}</span>
                                ) : (
                                  <span className="text-gray-500 italic">not set</span>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    <div className={`flex gap-2 ${viewMode === 'grid' ? 'mt-4' : ''}`}>
                      <button
                        onClick={() => handleEdit(member)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(member.id)}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}