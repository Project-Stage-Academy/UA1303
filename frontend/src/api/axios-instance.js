import axios from 'axios';
import { API_BASE_URL, ENDPOINTS } from './config';
import { getAccessToken, getRefreshToken, setAccessToken } from '../utils/auth';

const axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  // Avoiding sending two requests in strict mode
  let isRefreshing = false; 
  let failedQueue = [];
  
  const processQueue = (error, token = null) => {
    failedQueue.forEach((promise) => {
      if (token) {
        promise.resolve(token);
      } else {
        promise.reject(error);
      }
    });
    failedQueue = [];
  };

  // Request Interceptor: Include Access Token
  axiosInstance.interceptors.request.use(
    (config) => {
      const accessToken = getAccessToken();
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );
  
  // Response Interceptor: Handle Token Refresh
  axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
  
      // If 401 error, try refreshing the token
      if (error.response && error.response.status === 401 && !originalRequest._retry) {
        if (isRefreshing) {
          // Push requests into queue while token is being refreshed
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return axiosInstance(originalRequest);
            })
            .catch((err) => Promise.reject(err));
        }
  
        originalRequest._retry = true;
        isRefreshing = true;
  
        try {
          const refreshToken = getRefreshToken();
  
          const response = await axios.post(
            `${API_BASE_URL}${ENDPOINTS.REFRESH_TOKEN}`,
            { refresh: refreshToken },
            { headers: { 'Content-Type': 'application/json' } }
          );
  
          const newAccessToken = response.data.access;
          setAccessToken(newAccessToken);
  
          // Process the queued requests with the new token
          processQueue(null, newAccessToken);
  
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return axiosInstance(originalRequest);
        } catch (refreshError) {
          processQueue(refreshError, null);
          console.error('Token refresh failed. Redirecting to login.');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }
  
      return Promise.reject(error);
    }
  );
  
  export default axiosInstance;