import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add loading indicators or auth tokens here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API functions
export const fetchHistoricalPrices = async (dateRange = {}) => {
  try {
    const params = new URLSearchParams();
    if (dateRange.start) params.append('start_date', dateRange.start);
    if (dateRange.end) params.append('end_date', dateRange.end);
    
    return await api.get(`/historical-prices?${params}`);
  } catch (error) {
    throw new Error('Failed to fetch historical prices');
  }
};

export const fetchEvents = async (category = 'All', minImpact = '1') => {
  try {
    const params = new URLSearchParams();
    if (category && category !== 'All') params.append('category', category);
    params.append('min_impact', minImpact);
    
    return await api.get(`/events?${params}`);
  } catch (error) {
    throw new Error('Failed to fetch events');
  }
};

export const fetchChangePoints = async () => {
  try {
    return await api.get('/change-points');
  } catch (error) {
    throw new Error('Failed to fetch change points');
  }
};

export const fetchVolatilityMetrics = async () => {
  try {
    return await api.get('/volatility-metrics');
  } catch (error) {
    throw new Error('Failed to fetch volatility metrics');
  }
};

export const fetchSummaryMetrics = async () => {
  try {
    return await api.get('/summary-metrics');
  } catch (error) {
    throw new Error('Failed to fetch summary metrics');
  }
};

export const fetchEventImpact = async (eventName) => {
  try {
    return await api.get(`/event-impact/${encodeURIComponent(eventName)}`);
  } catch (error) {
    throw new Error('Failed to fetch event impact details');
  }
};

export const healthCheck = async () => {
  try {
    return await api.get('/health');
  } catch (error) {
    throw new Error('API health check failed');
  }
};

export default api;