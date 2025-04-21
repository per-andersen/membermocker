import React, { useState } from 'react';
import MemberForm from '../components/MemberForm';

export default function DataSetPage() {
  const [member, setMember] = useState(null);
  return (
    <div>
      <MemberForm onData={setMember} />
      {member && (
        <div className="mt-4 p-4 border rounded">
          <h2 className="text-xl font-bold mb-2">Generated Member:</h2>
          <ul>
            <li>Name: {member.first_name} {member.surname}</li>
            <li>Email: {member.email}</li>
            <li>Phone: {member.phone_number}</li>
            <li>Address: {member.address}</li>
            <li>Birthday: {new Date(member.birthday).toLocaleDateString()}</li>
            <li>Join Date: {new Date(member.date_member_joined_group).toLocaleDateString()}</li>
          </ul>
        </div>
      )}
    </div>
  );
}