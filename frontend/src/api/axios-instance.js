import axios from 'axios';
import { API_BASE_URL} from './config';
import { getAccessToken, refreshToken} from '../utils/auth';

const axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
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
        originalRequest._retry = true;
  
        try {
          const newAccessToken = await refreshToken();
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return axiosInstance(originalRequest);
        } catch (refreshError) {
          console.error('Token refresh failed. Redirecting to login.');
          window.location.href = '/';
          return Promise.reject(refreshError);
        }
      }
  
      return Promise.reject(error);
    }
  );
  
  export default axiosInstance;