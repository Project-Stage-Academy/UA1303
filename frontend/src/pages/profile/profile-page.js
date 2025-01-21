import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ENDPOINTS } from '../../api/config';
import axiosInstance from '../../api/axios-instance';
import './profile-page.css';

const ProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axiosInstance.get(ENDPOINTS.ME);
        const data = response.data;
        setProfile(data);
      } catch (err) {
        setError(err.message);
        localStorage.removeItem('accessToken'); // Clear token on failure
        navigate('/'); // Redirect to login page
      }
    };

    fetchProfile();
  }, [navigate]);

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!profile) {
    return <div>Loading...</div>;
  }

  return (
    <div className='container'>
      <h1>User Profile</h1>
      <p><strong>User ID:</strong> {profile.user_id}</p>
      <p><strong>Name:</strong> {profile.first_name} {profile.last_name}</p>
      <p><strong>Email:</strong> {profile.email}</p>
      <p><strong>Phone:</strong> {profile.user_phone}</p>
      <p><strong>Role:</strong> {profile.role_name}</p>
      <p><strong>Title:</strong> {profile.title}</p>
      <p><strong>Created At:</strong> {new Date(profile.created_at).toLocaleString()}</p>
      <p><strong>Updated At:</strong> {new Date(profile.updated_at).toLocaleString()}</p>
    </div>
  );
};
  
  export default ProfilePage;