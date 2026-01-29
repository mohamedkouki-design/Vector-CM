import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchSimilar = async (clientData, topK = 50) => {
  const response = await api.post('/search/similar', {
    client_data: clientData,
    top_k: topK
  });
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/search/stats');
  return response.data;
};

export default api;