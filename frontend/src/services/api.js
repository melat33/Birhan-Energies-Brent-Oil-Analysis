import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor for adding auth tokens, etc.
api.interceptors.request.use(
  (config) => {
    // Add any request headers here
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request timestamp for debugging
    config.headers['X-Request-Timestamp'] = new Date().toISOString();
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const { response } = error;
    
    // Handle different error statuses
    if (response) {
      switch (response.status) {
        case 401:
          console.error('Unauthorized access');
          break;
        case 403:
          console.error('Forbidden access');
          break;
        case 404:
          console.error('Resource not found');
          break;
        case 500:
          console.error('Internal server error');
          break;
        case 503:
          console.error('Service unavailable');
          break;
        default:
          console.error('API error:', error.message);
      }
    } else if (error.code === 'ECONNABORTED') {
      console.error('Request timeout');
    } else if (error.code === 'ERR_NETWORK') {
      console.error('Network error');
    }
    
    // Return structured error
    return Promise.reject({
      success: false,
      message: error.response?.data?.message || error.message,
      status: error.response?.status,
      data: error.response?.data
    });
  }
);

// Cache mechanism for API responses
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

const getCacheKey = (url, params) => {
  const paramString = params ? JSON.stringify(params) : '';
  return `${url}:${paramString}`;
};

const getFromCache = (key) => {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  cache.delete(key);
  return null;
};

const setToCache = (key, data) => {
  cache.set(key, {
    data,
    timestamp: Date.now()
  });
};

// API functions with caching
export const healthCheck = async () => {
  const cacheKey = getCacheKey('/health');
  const cached = getFromCache(cacheKey);
  if (cached) return cached;
  
  const response = await api.get('/health');
  setToCache(cacheKey, response);
  return response;
};

export const fetchPrices = async (params = {}) => {
  const cacheKey = getCacheKey('/prices', params);
  const cached = getFromCache(cacheKey);
  if (cached) return cached;
  
  const response = await api.get('/prices', { params });
  setToCache(cacheKey, response);
  return response;
};

export const fetchEvents = async (params = {}) => {
  const cacheKey = getCacheKey('/events', params);
  const cached = getFromCache(cacheKey);
  if (cached) return cached;
  
  const response = await api.get('/events', { params });
  setToCache(cacheKey, response);
  return response;
};

export const fetchChangePoints = async () => {
  const cacheKey = getCacheKey('/change-points');
  const cached = getFromCache(cacheKey);
  if (cached) return cached;
  
  const response = await api.get('/change-points');
  setToCache(cacheKey, response);
  return response;
};

export const fetchMetrics = async () => {
  const cacheKey = getCacheKey('/metrics');
  const cached = getFromCache(cacheKey);
  if (cached) return cached;
  
  const response = await api.get('/metrics');
  setToCache(cacheKey, response);
  return response;
};

export const fetchSummaryMetrics = async () => {
  const cacheKey = getCacheKey('/metrics');
  const cached = getFromCache(cacheKey);
  if (cached) return cached;
  
  const response = await api.get('/metrics');
  setToCache(cacheKey, response);
  return response;
};

export const fetchEventImpact = async (eventName) => {
  const response = await api.get(`/analysis/event-impact/${encodeURIComponent(eventName)}`);
  return response;
};

export const fetchSeasonality = async () => {
  const cacheKey = getCacheKey('/analysis/seasonality');
  const cached = getFromCache(cacheKey);
  if (cached) return cached;
  
  const response = await api.get('/analysis/seasonality');
  setToCache(cacheKey, response);
  return response;
};

export const fetchDashboardConfig = async () => {
  const response = await api.get('/config');
  return response;
};

// Export data functions
export const exportPrices = async (format = 'csv') => {
  const response = await api.get(`/export/prices?format=${format}`, {
    responseType: 'blob'
  });
  return response;
};

export const exportEvents = async (format = 'json') => {
  const response = await api.get(`/export/events?format=${format}`, {
    responseType: 'blob'
  });
  return response;
};

// Clear cache function
export const clearCache = () => {
  cache.clear();
};

// Batch requests for efficiency
export const batchRequests = async (requests) => {
  const results = await Promise.allSettled(requests);
  return results.map((result, index) => ({
    request: requests[index],
    status: result.status,
    data: result.status === 'fulfilled' ? result.value : result.reason,
    error: result.status === 'rejected' ? result.reason : null
  }));
};

export default api;