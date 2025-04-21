import React, { useState } from 'react';
import { updateMember, deleteMember, downloadMembers } from '../services/api';

export default function MemberList({ members, onMemberDeleted, onMemberUpdated }) {
  const [editingMember, setEditingMember] = useState(null);
  const [editForm, setEditForm] = useState({});

  const handleEdit = (member) => {
    setEditingMember(member.id);
    setEditForm(member);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setEditForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = async (id) => {
    try {
      const updated = await updateMember(id, editForm);
      setEditingMember(null);
      onMemberUpdated(updated);
    } catch (error) {
      console.error('Error updating member:', error);
      alert('Failed to update member. Please try again.');
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
    return <p className="text-gray-500 text-center py-4">No members generated yet.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end gap-2">
        <button
          onClick={() => handleDownload('csv')}
          className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Download CSV
        </button>
        <button
          onClick={() => handleDownload('excel')}
          className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Download Excel
        </button>
      </div>
      <div className="grid gap-4">
        {members.map(member => (
          <div key={member.id} className="p-4 bg-white rounded shadow">
            {editingMember === member.id ? (
              <div className="space-y-2">
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="text"
                    name="first_name"
                    value={editForm.first_name}
                    onChange={handleChange}
                    className="border rounded px-2 py-1"
                    placeholder="First Name"
                  />
                  <input
                    type="text"
                    name="surname"
                    value={editForm.surname}
                    onChange={handleChange}
                    className="border rounded px-2 py-1"
                    placeholder="Surname"
                  />
                  <input
                    type="email"
                    name="email"
                    value={editForm.email}
                    onChange={handleChange}
                    className="border rounded px-2 py-1"
                    placeholder="Email"
                  />
                  <input
                    type="tel"
                    name="phone_number"
                    value={editForm.phone_number}
                    onChange={handleChange}
                    className="border rounded px-2 py-1"
                    placeholder="Phone"
                  />
                  <input
                    type="text"
                    name="address"
                    value={editForm.address}
                    onChange={handleChange}
                    className="border rounded px-2 py-1 col-span-2"
                    placeholder="Address"
                  />
                  <input
                    type="date"
                    name="birthday"
                    value={editForm.birthday}
                    onChange={handleChange}
                    className="border rounded px-2 py-1"
                  />
                  <input
                    type="date"
                    name="date_member_joined_group"
                    value={editForm.date_member_joined_group}
                    onChange={handleChange}
                    className="border rounded px-2 py-1"
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => setEditingMember(null)}
                    className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleSave(member.id)}
                    className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Save
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold">{member.first_name} {member.surname}</h3>
                    <p className="text-gray-600">{member.email}</p>
                    <p className="text-gray-600">{member.phone_number}</p>
                    <p className="text-gray-600">{member.address}</p>
                    <p className="text-sm text-gray-500">
                      Born: {new Date(member.birthday).toLocaleDateString()}
                    </p>
                    <p className="text-sm text-gray-500">
                      Joined: {new Date(member.date_member_joined_group).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(member)}
                      className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(member.id)}
                      className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
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
    </div>
  );
}