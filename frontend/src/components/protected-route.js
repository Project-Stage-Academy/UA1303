import { Navigate } from 'react-router-dom';
import { getAuthStatus } from '../utils/auth';

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { isAuthenticated, role } = getAuthStatus();

  // Redirect to login if the user is not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login/" />;
  }

  // Check access
  if (!allowedRoles.includes(role)) {
    return <Navigate to="/unauthorized/" />;
  }

  return children; // Render the protected page
};

export default ProtectedRoute;