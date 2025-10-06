/**
 * API service for communicating with the FastAPI backend.
 * Handles all HTTP requests and error handling.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Submit a question to the RAG system
 * @param {string} query - User's question
 * @param {boolean} includeSources - Whether to include source FAQs
 * @returns {Promise} API response with answer and sources
 */
export const askQuestion = async (query, includeSources = true) => {
  try {
    const response = await api.post('/api/ask', {
      query,
      include_sources: includeSources,
    });
    return response.data;
  } catch (error) {
    console.error('Error asking question:', error);
    throw error;
  }
};

/**
 * Fetch interaction logs
 * @param {number} limit - Maximum number of logs to retrieve
 * @returns {Promise} Array of log entries
 */
export const getInteractionLogs = async (limit = 50) => {
  try {
    const response = await api.get(`/api/logs?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching logs:', error);
    throw error;
  }
};

/**
 * Get system statistics
 * @returns {Promise} Statistics object
 */
export const getStatistics = async () => {
  try {
    const response = await api.get('/api/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching statistics:', error);
    throw error;
  }
};

/**
 * Check system health
 * @returns {Promise} Health status object
 */
export const checkHealth = async () => {
  try {
    const response = await api.get('/api/health');
    return response.data;
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
};

export default api;
