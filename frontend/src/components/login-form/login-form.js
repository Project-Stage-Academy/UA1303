import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../../api/axios-instance';
import Button from '../button/button';
import Form from '../input-form/input-form';
import './login-form.css';
import { ENDPOINTS } from '../../api/config';
import { setAccessToken, setRefreshToken } from '../../utils/auth';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Startup'); // Default role
  const [error, setError] = useState(null); // Error handling
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Determine the role value (1 for Startup, 2 for Investor)
    const roleValue = role === 'Startup' ? 1 : 2;
    // Prepare the request payload
    const payload = {
      role: roleValue,
      email,
      password,
    };

    try {
      const response = await axiosInstance.post(ENDPOINTS.LOGIN, payload);
      const data = response.data;

      // Save JWT tokens
      setAccessToken(data.access);
      setRefreshToken(data.refresh);

      // Redirect to the profile page
      navigate('/my_profile/');
    } catch (error) {
      setError(error.message || 'Something went wrong. Please try again.');
    }
  };


    return (
      <Form
      headerText="Login"
      onSubmit={handleSubmit}
      footerContent={<Button text="Sign In" variant="primary" />}
      >
        {error && <p className="error">{error}</p>}

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Role:</label>
          <div>
            <label>
              <input
                type="radio"
                name="role"
                value="Startup"
                checked={role === 'Startup'}
                onChange={(e) => setRole(e.target.value)}
              />
              Startup
            </label>
            <label>
              <input
                type="radio"
                name="role"
                value="Investor"
                checked={role === 'Investor'}
                onChange={(e) => setRole(e.target.value)}
              />
              Investor
            </label>
          </div>
        </div>
      </Form>
    );
};

export default LoginForm;