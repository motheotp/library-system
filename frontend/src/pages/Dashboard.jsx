import { useState, useEffect } from 'react';
import { borrowingAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

function Dashboard() {
  const [borrowedBooks, setBorrowedBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchBorrowedBooks();
    }
  }, [user]);

  const fetchBorrowedBooks = async () => {
    try {
      setLoading(true);
      const response = await borrowingAPI.getUserBorrowedBooks(user.id);
      setBorrowedBooks(response.data.borrowed_books);
    } catch (err) {
      setError('Failed to load borrowed books');
    } finally {
      setLoading(false);
    }
  };

  const handleReturn = async (borrowingId) => {
    try {
      const response = await borrowingAPI.returnBook(borrowingId);
      const returnedBook = response.data.borrowing;

      if (returnedBook.fine_amount > 0) {
        setSuccessMessage(
          `Book returned! Fine amount: $${returnedBook.fine_amount.toFixed(2)}`
        );
      } else {
        setSuccessMessage('Book returned successfully!');
      }

      setTimeout(() => setSuccessMessage(''), 5000);
      fetchBorrowedBooks(); // Refresh the list
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to return book');
      setTimeout(() => setError(''), 3000);
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
    return <div className="loading">Loading your borrowed books...</div>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>My Dashboard</h1>
        <div className="user-info">
          <p>👤 {user.name}</p>
          <p className="student-id">ID: {user.student_id}</p>
          <p className="role">{user.role}</p>
        </div>
      </div>

      {(error || successMessage) && (
        <div className={`message ${error ? 'error' : 'success'}`}>
          {error || successMessage}
        </div>
      )}

      <div className="borrowed-section">
        <h2>Currently Borrowed Books ({borrowedBooks.length})</h2>

        {borrowedBooks.length === 0 ? (
          <div className="empty-state">
            <p>📚 You haven't borrowed any books yet.</p>
            <p>Visit the library catalog to borrow books!</p>
          </div>
        ) : (
          <div className="borrowed-grid">
            {borrowedBooks.map(({ borrowing, book, days_remaining }) => (
              <div key={borrowing.id} className="borrowed-card">
                <div className="book-info">
                  <h3>{book.title}</h3>
                  <p className="author">by {book.author}</p>
                  <p className="category">{book.category}</p>
                </div>

                <div className="borrowing-details">
                  <div className="detail-row">
                    <span className="label">Borrowed:</span>
                    <span>{formatDate(borrowing.borrowed_date)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Due Date:</span>
                    <span className={borrowing.is_overdue ? 'overdue' : ''}>
                      {formatDate(borrowing.due_date)}
                    </span>
                  </div>
                  {borrowing.is_overdue ? (
                    <div className="overdue-badge">
                      ⚠️ Overdue by {borrowing.days_overdue} days
                    </div>
                  ) : (
                    <div className={`days-remaining ${days_remaining <= 3 ? 'warning' : ''}`}>
                      {days_remaining} days remaining
                    </div>
                  )}
                </div>

                <button
                  className="btn-return"
                  onClick={() => handleReturn(borrowing.id)}
                >
                  Return Book
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="borrowing-limit">
        <p>📖 You can borrow up to 3 books at a time</p>
        <p>Current: {borrowedBooks.length} / 3</p>
      </div>
    </div>
  );
}

export default Dashboard;
