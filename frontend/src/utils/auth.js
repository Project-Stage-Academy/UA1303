const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  };

export const getAccessToken = () => {
    const accessToken = getCookie('accessToken');
    const tempAccessToken = localStorage.getItem('access_token');
    if (accessToken) {
        return accessToken;
    } else if (tempAccessToken){
        return tempAccessToken;
    } else {
        return null;
    }
};

export const getRefreshToken = () => {
    const refreshToken = getCookie('refreshToken');
    if (refreshToken) {
        return refreshToken;
    } else {
        throw new Error('No refresh token available');
    }
};

export const setAccessToken = (accessToken) => {
    document.cookie = `accessToken=${accessToken}; path=/; max-age=1200; Secure; SameSite=Strict`;
};

export const setRefreshToken = (refreshToken) => {
    document.cookie = `refreshToken=${refreshToken}; path=/; max-age=86400; Secure; SameSite=Strict`;
};