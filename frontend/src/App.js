import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/protected-route';
import Layout from './components/layout/layout';
import LoginPage from './pages/login/login-page';
import ProfilePage from './pages/profile/profile-page';
import OAuthCallback from './pages/socialauth-callback/socialauth-callback';
import ChooseRole from './pages/choose-role/choose-role';
import Home from './pages/home/home';
import UnauthorizedPage from './pages/unauthorized/unauthorized';
import StartupsListPage from './pages/startups-list/startups-list';



function App() {
  return (
    <Router>
    <Layout>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login/" element={<LoginPage />} />
        <Route path="/oauth2callback/" element={<OAuthCallback />} />
        <Route path="/unauthorized/" element={<UnauthorizedPage />} />

        {/* Protected Routes */}
        <Route
            path="/my_profile/"
            element={
              <ProtectedRoute allowedRoles={['startup', 'investor']}>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/choose_role/"
            element={
              <ProtectedRoute allowedRoles={['startup', 'investor']}>
                <ChooseRole />
              </ProtectedRoute>
            }
          />
          <Route
            path="/startups/"
            element ={
              <ProtectedRoute allowedRoles={['investor']}>
                <StartupsListPage />
              </ProtectedRoute>
            }
          />
      </Routes>
    </Layout>
    </Router>
  );
}

export default App;
