import axios from 'axios';

const API = axios.create({ baseURL: 'http://localhost:8000' });

export const generateMembers = async (config) => {
  const response = await API.post('/generate', config);
  return response.data;
};

export const listMembers = async () => {
  const response = await API.get('/members');
  return response.data;
};

export const getMember = async (id) => {
  const response = await API.get(`/members/${id}`);
  return response.data;
};

export const updateMember = async (id, data) => {
  const response = await API.patch(`/members/${id}`, data);
  return response.data;
};

export const deleteMember = async (id) => {
  await API.delete(`/members/${id}`);
};

export const downloadMembers = async (format) => {
  const response = await API.get(`/download/${format}`, {
    responseType: 'blob'
  });
  
  // Map format to correct file extension
  const extension = format.toLowerCase() === 'excel' ? 'xlsx' : format;
  
  // Create a download link and trigger it
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `members.${extension}`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};