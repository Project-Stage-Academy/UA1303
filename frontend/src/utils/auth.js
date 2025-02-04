import axios from 'axios';
import { API_BASE_URL, ENDPOINTS } from '../api/config';
import { getRoleName } from './roles';
import axiosInstance from '../api/axios-instance';


const getCookie = (name) => {
    return document.cookie
        .split(';')
        .map((cookie) => cookie.trim())
        .find((cookie) => cookie.startsWith(`${name}=`))
        ?.split('=')[1];
};


const isTokenExpired = (token) => {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp * 1000 < Date.now();
    } catch {
        return true; // Invalid token
    }
};

export const handleLogout = async (navigate) => {
    try {
      const refreshToken = getRefreshToken();
      const payload = { 'refresh': refreshToken };
      await axiosInstance.post(ENDPOINTS.LOGOUT, payload);
      cleanTokens();
      navigate('/');
    } catch (err) {
      console.error('Logout failed:', err);
    }
};

export const getAccessToken = () => {
    const token = getCookie('accessToken') || localStorage.getItem('access_token');
    return token && !isTokenExpired(token) ? token : null;
};

export const getRefreshToken = () => {
    const refreshToken = getCookie('refreshToken');
    return refreshToken || null;
};

export const setAccessToken = (accessToken) => {
    document.cookie = `accessToken=${accessToken}; path=/; max-age=1200; Secure; SameSite=Strict`;
};

export const setRefreshToken = (refreshToken) => {
    document.cookie = `refreshToken=${refreshToken}; path=/; max-age=86400; Secure; SameSite=Strict`;
};

export const cleanTokens = () => {
    document.cookie = 'accessToken=; path=/; max-age=0; Secure; SameSite=Strict';
    localStorage.removeItem('access_token');
    
    document.cookie = 'refreshToken=; path=/; max-age=0; Secure; SameSite=Strict';
    localStorage.removeItem('refresh_token');
};

export const refreshToken = async () => {
    const refreshToken = getRefreshToken();
  
    if (!refreshToken) {
        console.error('No refresh token available. Redirecting to login.');
        alert('Your session has expired. Please log in again.');
        window.location.href = '/';
        return Promise.reject(new Error('No refresh token available.'));
    }
    try {
        const response = await axios.post(
            `${API_BASE_URL}${ENDPOINTS.REFRESH_TOKEN}`,
            { refresh: refreshToken },
            { headers: {
                'Content-Type': 'application/json' ,
                'Accept': 'application/json',
              },
            }
        );
        
        const newAccessToken = response.data.access;
        const newRefreshToken = response.data.refresh;
        setAccessToken(newAccessToken);
        setRefreshToken(newRefreshToken);
        return newAccessToken;
    } catch (error) {
        console.error('Failed to refresh token:', error);
        window.location.href = '/';
        return Promise.reject(new Error('Failed to refresh token.'));
    }
};

export const getAuthStatus = () => {
    const accessToken = getAccessToken();
    const refreshToken = getRefreshToken();
    if (refreshToken && isTokenExpired(refreshToken)) {
        cleanTokens()
        return { isAuthenticated: false, role: null };
    }
    
    if (!accessToken && !refreshToken) {
        return { isAuthenticated: false, role: null };
    }
    const token = accessToken || refreshToken;
    try {
        const payload = JSON.parse(atob(token.split('.')[1])); // Decode JWT payload
        const role = getRoleName(payload.role); // Convert role into human-readable format
        return { isAuthenticated: true, role };
    } catch (error) {
        console.error('Failed to parse token payload:', error);
        return { isAuthenticated: false, role: null };
    }
  };