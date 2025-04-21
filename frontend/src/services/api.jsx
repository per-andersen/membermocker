import axios from 'axios';

const API = axios.create({ baseURL: 'http://localhost:8000' });

export const generateMembers = async (config) => {
  const response = await API.post('/generate', config);
  return response.data;
};