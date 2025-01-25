import './navbar.css';

import { useNavigate } from 'react-router-dom';
import { getAuthStatus, handleLogout } from '../../utils/auth';

const Navbar = () => {
  const navigate = useNavigate();

  const { isAuthenticated, role } = getAuthStatus();

  // Define dynamic links based on authentication and role
  const links = [];
  if (!isAuthenticated) {
    links.push({ name: 'Login', path: '/login/' });
  } else if (role === 'startup') {
    links.push({ name: 'My Profile', path: '/my_profile/' });
    links.push({ 
      name : 'Logout',
      action: () => handleLogout(navigate),
      icon: 'fa-solid fa-right-from-bracket'  // Add Font Awesome icon class
    });
    // Add message inbox in the future
  } else if (role === 'investor') {
    links.push({ name: 'My Profile', path: '/my_profile/' });
    links.push({ name: 'Startups', path: '/startups/' });
    links.push({ 
      name : 'Logout',
      action: () => handleLogout(navigate),
      icon: 'fa-solid fa-right-from-bracket'  // Add Font Awesome icon class
    });
  }

  return (
    <nav className="navbar">
      <div className="navbar-logo" onClick={() => navigate('/')}>
        FORUM App
      </div>
      <ul className="navbar-menu">
        {links.map((link) => (
          <li key={link.name}>
            {link.path ? (
              <a href={link.path}>{link.name}</a>
            ) : (
            <button onClick={link.action} className="navbar-logout-button" title="Logout">
              <i className={link.icon}></i>
              {link.name && <span>{link.name}</span>}
            </button>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
};


export default Navbar;