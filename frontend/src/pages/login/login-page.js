import LoginForm from '../../components/login-form/login-form';
import SocialLoginform from '../../components/social-login-form/social-login-form';
import { Navigate } from 'react-router-dom';
import { getAuthStatus } from '../../utils/auth';


const LoginPage = () => {
    const { isAuthenticated, role } = getAuthStatus();

    if (isAuthenticated) {
        return <Navigate to="/my_profile/" />;
    }

    return (
        <div>
            <LoginForm />
            <SocialLoginform />
        </div>
    );
};

export default LoginPage;