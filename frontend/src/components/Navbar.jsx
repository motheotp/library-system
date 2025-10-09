import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

function Navbar() {
  const { user, isAuthenticated, isLibrarian, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          📚 Library System
        </Link>

        <div className="nav-menu">
          <Link to="/" className="nav-link">
            Books
          </Link>

          {isAuthenticated && (
            <>
              <Link to="/dashboard" className="nav-link">
                My Books
              </Link>

              {isLibrarian && (
                <Link to="/admin" className="nav-link">
                  Admin
                </Link>
              )}
            </>
          )}
        </div>

        <div className="nav-actions">
          {isAuthenticated ? (
            <>
              <span className="user-name">👤 {user.name}</span>
              <button onClick={handleLogout} className="btn-logout">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-login">
                Login
              </Link>
              <Link to="/register" className="btn-register">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
