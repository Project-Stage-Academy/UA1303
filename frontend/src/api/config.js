    const API_HOST_URL = process.env.REACT_APP_API_BASE_URL;
    const BASE_PREFIX = 'api/v1/';
    export const API_BASE_URL = API_HOST_URL + BASE_PREFIX;

export const ENDPOINTS = {
    LOGIN: `auth/login/`,
    LOGOUT: `auth/logout/`,
    REGISTER: `auth/user-register/`,
    PASSWORD_RESET: `auth/password/reset/`,
    REFRESH_TOKEN: `auth/token/refresh/`,
    ME: `auth/me/`,

    CONVERT_TOKEN: `${API_HOST_URL}auth/convert-token`,
    GITHUB_TOKEN: `auth/github-token/`,
    CHANGE_ROLE: `auth/change-role/`,
}