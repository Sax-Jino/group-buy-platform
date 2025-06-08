const API_BASE_URL = '/api';

const apiRequest = async (endpoint, method = 'GET', data = null, token = null) => {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    method,
    headers,
  };

  if (data) {
    config.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || 'Request failed');
    }
    return result;
  } catch (error) {
    throw error;
  }
};

export const login = (email, password) =>
  apiRequest('/auth/login', 'POST', { email, password });

export const getProfile = (token) =>
  apiRequest('/auth/me', 'GET', null, token);

export const getProducts = () =>
  apiRequest('/products');

export const getOrders = (token) =>
  apiRequest('/orders/user', 'GET', null, token);

export const getProposals = () =>
  apiRequest('/collaboration/proposals');

export const fetchWithToken = (endpoint, method = 'GET', data = null, token) =>
  apiRequest(endpoint, method, data, token);

export default apiRequest;