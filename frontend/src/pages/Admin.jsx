import { useState, useEffect } from 'react';
import { adminAPI, borrowingAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Admin.css';

function Admin() {
  const [stats, setStats] = useState(null);
  const [overdueBooks, setOverdueBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user, isLibrarian } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLibrarian) {
      navigate('/');
      return;
    }
    fetchData();
  }, [isLibrarian, navigate]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsResponse, overdueResponse] = await Promise.all([
        adminAPI.getStatistics(),
        borrowingAPI.getOverdueBooks(),
      ]);

      setStats(statsResponse.data);
      setOverdueBooks(overdueResponse.data.overdue_books);
    } catch (err) {
      setError('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return <div className="loading">Loading admin dashboard...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>📊 Admin Dashboard</h1>
        <p className="welcome">Welcome, {user?.name}</p>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📚</div>
            <div className="stat-content">
              <h3>Total Books</h3>
              <p className="stat-number">{stats.books.total}</p>
              <div className="stat-details">
                <span className="detail-item available">
                  {stats.books.available} available
                </span>
                <span className="detail-item borrowed">
                  {stats.books.borrowed} borrowed
                </span>
              </div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <div className="stat-content">
              <h3>Users</h3>
              <p className="stat-number">{stats.users.total}</p>
              <div className="stat-details">
                <span className="detail-item">
                  {stats.users.students} students
                </span>
                <span className="detail-item">
                  {stats.users.librarians} librarians
                </span>
              </div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📖</div>
            <div className="stat-content">
              <h3>Borrowings</h3>
              <p className="stat-number">{stats.borrowings.total}</p>
              <div className="stat-details">
                <span className="detail-item active">
                  {stats.borrowings.active} active
                </span>
                <span className="detail-item overdue">
                  {stats.borrowings.overdue} overdue
                </span>
              </div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🔖</div>
            <div className="stat-content">
              <h3>Reservations</h3>
              <p className="stat-number">{stats.reservations.active}</p>
              <div className="stat-details">
                <span className="detail-item">Active reservations</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="overdue-section">
        <h2>⚠️ Overdue Books ({overdueBooks.length})</h2>

        {overdueBooks.length === 0 ? (
          <div className="empty-state">
            <p>✅ No overdue books! Everything is running smoothly.</p>
          </div>
        ) : (
          <div className="overdue-table">
            <table>
              <thead>
                <tr>
                  <th>Book</th>
                  <th>Borrower</th>
                  <th>Student ID</th>
                  <th>Due Date</th>
                  <th>Days Overdue</th>
                  <th>Contact</th>
                </tr>
              </thead>
              <tbody>
                {overdueBooks.map(({ borrowing, book, user }) => (
                  <tr key={borrowing.id}>
                    <td>
                      <div className="book-cell">
                        <strong>{book.title}</strong>
                        <small>{book.author}</small>
                      </div>
                    </td>
                    <td>{user.name}</td>
                    <td>{user.student_id}</td>
                    <td>{formatDate(borrowing.due_date)}</td>
                    <td>
                      <span className="overdue-badge">
                        {borrowing.days_overdue} days
                      </span>
                    </td>
                    <td>
                      <a href={`mailto:${user.email}`}>{user.email}</a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {stats && (
        <div className="timestamp">
          Last updated: {new Date(stats.generated_at).toLocaleString()}
        </div>
      )}
    </div>
  );
}

export default Admin;
