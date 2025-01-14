import Button from '../button/button';
import './social-login-form.css';

const SocialLoginForm = () => {

  const googleClientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;
  const githubClientId = process.env.REACT_APP_GITHUB_CLIENT_ID;
  const redirectUri = process.env.REACT_APP_REDIRECT_URI;
  const googleScopes = 'profile email';
  const githubScopes = ['read:user', 'user:email'];

  const handleSocialLogin = (provider) => {
    let oauthURL;

    if (provider === 'google') {
      oauthURL = `https://accounts.google.com/o/oauth2/v2/auth?` +
        `client_id=${googleClientId}` +
        `&redirect_uri=${encodeURIComponent(redirectUri)}` +
        `&response_type=token` +
        `&scope=${encodeURIComponent(googleScopes)}`;
    } else if (provider === 'github') {
      oauthURL = `https://github.com/login/oauth/authorize?` +
        `client_id=${githubClientId}` +
        `&redirect_uri=${encodeURIComponent(redirectUri)}` +
        `&scope=${encodeURIComponent(githubScopes.join(' '))}`;
    }

    // Redirect to the generated OAuth URL
    window.location.href = oauthURL;
  };

  return (
    <div className='social-login-form'>
      <div className='form-footer' id='social-login-buttons'>
        <Button text='Google login' onClick={() => handleSocialLogin('google')} />
        <Button text='Github login' onClick={() => handleSocialLogin('github')} />
      </div>
    </div>
  );
};

export default SocialLoginForm;
