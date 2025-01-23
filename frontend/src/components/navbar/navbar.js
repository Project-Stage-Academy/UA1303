import './navbar.css';

import { useNavigate } from 'react-router-dom';
import { getAuthStatus } from '../../utils/auth';

const Navbar = () => {
  const navigate = useNavigate();

  const { isAuthenticated, role } = getAuthStatus();

  // Define dynamic links based on authentication and role
  const links = [];
  if (!isAuthenticated) {
    links.push({ name: 'Login', path: '/login/' });
  } else if (role === 'startup') {
    links.push({ name: 'My Profile', path: '/my_profile/' });
    // Add message inbox in the future
  } else if (role === 'investor') {
    links.push({ name: 'My Profile', path: '/my_profile/' });
    links.push({ name: 'Startups', path: '/startups/' });
  }

  return (
    <nav className="navbar">
      <div className="navbar-logo" onClick={() => navigate('/')}>
        FORUM App
      </div>
      <ul className="navbar-menu">
        {links.map((link) => (
          <li key={link.name}>
            <a href={link.path}>{link.name}</a>
          </li>
        ))}
      </ul>
    </nav>
  );
};


export default Navbar;