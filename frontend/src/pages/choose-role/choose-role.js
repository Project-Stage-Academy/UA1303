import { ENDPOINTS } from '../../api/config';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Form from '../../components/input-form/input-form';
import Button from '../../components/button/button';
import ToggleButtonGroup from '../../components/toggle-button-group/toggle-button-group';
import './choose-role.css';


const ChooseRole = () => {

    const [selectedRole, setSelectedRole] = useState(1); // Default to "Startup" (1)
    const navigate = useNavigate();
    const url = `${ENDPOINTS.CHANGE_ROLE}`;

    const handleConfirm = async () => {
        const accessToken = localStorage.getItem('access_token'); // Get token from localStorage
        if (!accessToken) {
          console.error('No access token found');
          navigate('/'); // Redirect to home if no token
          return;
        }
    
        try {
          const response = await fetch(url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${accessToken}`, // Include drf-social-oauth2 token in Authorization header
            },
            body: JSON.stringify({ role: selectedRole }),
          });
    
          if (!response.ok) {
            throw new Error('Failed to change role');
          }
          
          const data = await response.json();

          // Save JWT tokens in localStorage
          localStorage.setItem('accessToken', data.access);
          localStorage.setItem('refreshToken', data.refresh);

          // Remove drf-social-oauth2 tokens from localStorage
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');

          // Redirect to profile page on success
          navigate('/my_profile/');
        } catch (error) {
          console.error(error.message);
          // Redirect to home page on error
          navigate('/');
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