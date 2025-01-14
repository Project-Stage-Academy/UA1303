export const getAuthHeaders = () => {
    const accessToken = localStorage.getItem('accessToken');
    return {
      Authorization: `Bearer ${accessToken}`,
    };
  };