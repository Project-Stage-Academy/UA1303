import LoginForm from '../../components/login-form/login-form';
import SocialLoginform from '../../components/social-login-form/social-login-form';


const LoginPage = () => {
    return (
        <div>
            <LoginForm />
            <SocialLoginform />
        </div>
    );
};

export default LoginPage;