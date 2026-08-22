import axios from 'axios';

const SIMULATION_TIMEOUT_MS = 3600000;

const api = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8080/api',
  timeout: SIMULATION_TIMEOUT_MS,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      error.message = 'Request timed out. Reduce the neuron count or the duration and run it again.';
    } else if (error.message === 'Network Error') {
      error.message = 'No response from the backend. Check that the server is running.';
    }
    return Promise.reject(error);
  }
);

export default api;
