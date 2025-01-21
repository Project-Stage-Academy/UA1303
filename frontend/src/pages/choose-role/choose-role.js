import { ENDPOINTS } from '../../api/config';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { setAccessToken, setRefreshToken } from '../../utils/auth';
import axiosInstance from '../../api/axios-instance';
import Form from '../../components/input-form/input-form';
import Button from '../../components/button/button';
import ToggleButtonGroup from '../../components/toggle-button-group/toggle-button-group';
import './choose-role.css';


const ChooseRole = () => {

    const [selectedRole, setSelectedRole] = useState(1); // Default to "Startup" (1)
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleConfirm = async () => {
      const payload = {
        role: selectedRole,
      };
        try {
          const response = await axiosInstance.post(ENDPOINTS.CHANGE_ROLE, payload);
          const data = response.data;

          // Save JWT tokens in cookies
          setAccessToken(data.access);
          setRefreshToken(data.refresh);

          // Remove drf-social-oauth2 tokens from localStorage
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');

          // Redirect to profile page on success
          navigate('/my_profile/');
        } catch (error) {
          setError(error.message || 'Something went wrong. Please try again.');
          // Redirect to home page on error
          // navigate('/');
        }
      };

    return (
        <Form
        headerText="Login"
        footerContent={<Button text="Confirm" variant="primary" onClick={(e) => { e.preventDefault(); handleConfirm(); }} />}
        >
            <ToggleButtonGroup 
                options={{ 1: 'Startup', 2: 'Investor' }}
                onChange={(roleId) => setSelectedRole(roleId)}
            />
        </Form>
    )
}

export default ChooseRole;