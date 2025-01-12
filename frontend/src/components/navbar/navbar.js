import './navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-logo">FORUM App</div>
      <ul className="navbar-menu">
        <li><a href="/">Home</a></li>
        <li><a href="/my_profile/">Profile</a></li>
      </ul>
    </nav>
  );
};

export default Navbar;