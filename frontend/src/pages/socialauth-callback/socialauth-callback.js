import { useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ENDPOINTS } from '../../api/config';


const OAuthCallback = () => {
  const hasProcessed = useRef(false); // Use a ref to avoid re-renders
  const navigate = useNavigate();
  const drfSocialOauthClientId = process.env.REACT_APP_SOCIALAUTH_CLIENT_ID;
  const redirectURI = process.env.REACT_APP_REDIRECT_URI;
  const convertTokenUrl = `${ENDPOINTS.CONVERT_TOKEN}`

  const saveTokensAndRedirect = useCallback((data) => {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    navigate('/choose_role');
  }, [navigate]);

  const handleGoogleFlow = useCallback(async (token) => {

    try {
      const response = await fetch(convertTokenUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          grant_type: 'convert_token',
          client_id: drfSocialOauthClientId,
          backend: 'google-oauth2',
          token: token,
        }),
      });

      if (!response.ok) {
        throw new Error(`Google token conversion failed: ${response.status}`);
      }

      const data = await response.json();
      saveTokensAndRedirect(data);
    } catch (error) {
      console.error('Error in Google flow:', error);
      navigate('/');
    }
  }, [navigate, saveTokensAndRedirect, convertTokenUrl, drfSocialOauthClientId]);

  const handleGithubFlow = useCallback(async (code) => {
    const githubTokenURL = `${ENDPOINTS.GITHUB_TOKEN}`

    try {
      const backendResponse = await fetch(githubTokenURL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code,
          redirect_uri: redirectURI,
        }),
      });

      if (!backendResponse.ok) {
        throw new Error(`GitHub token exchange failed: ${backendResponse.status}`);
      }

      const responseData = await backendResponse.json();
      const githubAccessToken = responseData.github_access_token;

      if (!githubAccessToken) {
        throw new Error('GitHub access token not found.');
      }

      const response = await fetch(convertTokenUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          grant_type: 'convert_token',
          client_id: drfSocialOauthClientId,
          backend: 'github',
          token: githubAccessToken,
        }),
      });

      if (!response.ok) {
        throw new Error(`GitHub token conversion failed: ${response.status}`);
      }

      const data = await response.json();
      saveTokensAndRedirect(data);
    } catch (error) {
      console.error('Error in GitHub flow:', error);
      navigate('/');
    }
  }, [navigate, saveTokensAndRedirect, convertTokenUrl, drfSocialOauthClientId, redirectURI]);

  useEffect(() => {
    if (hasProcessed.current) return; // Prevent multiple executions

    const hashParams = new URLSearchParams(window.location.hash.slice(1));
    const searchParams = new URLSearchParams(window.location.search);

    const googleToken = hashParams.get('access_token');
    const githubCode = searchParams.get('code');

    if (googleToken) {
      hasProcessed.current = true;
      handleGoogleFlow(googleToken);
    } else if (githubCode) {
      hasProcessed.current = true;
      handleGithubFlow(githubCode);
    } else {
      console.error('No valid token or code found in URL.');
      navigate('/');
    }
  }, [handleGoogleFlow, handleGithubFlow, navigate]);

  return <div>Processing your login...</div>;
};

export default OAuthCallback;