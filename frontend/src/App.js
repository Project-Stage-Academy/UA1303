import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/layout';
import LoginPage from './pages/login/login-page';
import ProfilePage from './pages/profile/profile-page';
import OAuthCallback from './pages/socialauth-callback/socialauth-callback';
import ChooseRole from './pages/choose-role/choose-role';



function App() {
  return (
    <Router>
    <Layout>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/my_profile/" element={<ProfilePage />} />
        <Route path="/oauth2callback/" element={<OAuthCallback />} />
        <Route path="/choose_role/" element = {<ChooseRole />} />
      </Routes>
    </Layout>
    </Router>
  );
}

export default App;
