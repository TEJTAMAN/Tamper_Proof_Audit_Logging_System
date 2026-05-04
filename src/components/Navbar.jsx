import { NavLink } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar">
      <NavLink to="/" className="navbar-brand">
        AuditChain
      </NavLink>
      <div className="navbar-links">
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/add-data">Add Data</NavLink>
        <NavLink to="/logs">Logs</NavLink>
        <NavLink to="/verify">Verify</NavLink>
        <NavLink to="/alerts">Alerts</NavLink>
        <NavLink to="/summary">Summary</NavLink>
      </div>
    </nav>
  );
};

export default Navbar;
