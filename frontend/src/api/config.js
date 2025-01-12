const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const BASE_PREFIX = 'api/v1/'

export const ENDPOINTS = {
    LOGIN: `${API_BASE_URL}${BASE_PREFIX}auth/login/`,
    LOGOUT: `${API_BASE_URL}${BASE_PREFIX}auth/logout/`,
    REGISTER: `${API_BASE_URL}${BASE_PREFIX}auth/user-register/`,
    PASSWORD_RESET: `${API_BASE_URL}${BASE_PREFIX}auth/password/reset/`,
    ME: `${API_BASE_URL}${BASE_PREFIX}auth/me/`,

    CONVERT_TOKEN: `${API_BASE_URL}auth/convert-token`,
    GITHUB_TOKEN: `${API_BASE_URL}${BASE_PREFIX}auth/github-token/`,
    CHANGE_ROLE: `${API_BASE_URL}${BASE_PREFIX}auth/change-role/`,
}