import { useState, useEffect } from 'react';
import { bookAPI, borrowingAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './Books.css';

function Books() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [category, setCategory] = useState('');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const { user } = useAuth();

  const categories = [
    'Programming',
    'Web Development',
    'Database',
    'Computer Science',
    'AI',
    'Software Engineering',
    'Architecture',
    'Systems',
    'Interview Prep',
  ];

  useEffect(() => {
    fetchBooks();
  }, [page, category]);

  const fetchBooks = async () => {
    try {
      setLoading(true);
      setError('');
      const params = { page, limit: 12 };
      if (category) params.category = category;

      const response = await bookAPI.getBooks(params);
      setBooks(response.data.books);
      setPagination(response.data.pagination);
    } catch (err) {
      setError('Failed to load books');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      fetchBooks();
      return;
    }

    try {
      setLoading(true);
      setError('');
      const response = await bookAPI.searchBooks(searchQuery);
      setBooks(response.data.books);
      setPagination({});
    } catch (err) {
      setError('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleBorrow = async (bookId) => {
    if (!user) {
      setError('Please login to borrow books');
      return;
    }

    try {
      await borrowingAPI.borrowBook(user.id, bookId);
      setSuccessMessage('Book borrowed successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
      fetchBooks(); // Refresh to update availability
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to borrow book');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleCategoryChange = (newCategory) => {
    setCategory(newCategory);
    setPage(1);
    setSearchQuery('');
  };

  return (
    <div className="books-container">
      <div className="books-header">
        <h1>📚 Library Catalog</h1>

        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search by title or author..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit">Search</button>
        </form>
      </div>

      {(error || successMessage) && (
        <div className={`message ${error ? 'error' : 'success'}`}>
          {error || successMessage}
        </div>
      )}

      <div className="filters">
        <button
          className={category === '' ? 'active' : ''}
          onClick={() => handleCategoryChange('')}
        >
          All Categories
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            className={category === cat ? 'active' : ''}
            onClick={() => handleCategoryChange(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="loading">Loading books...</div>
      ) : books.length === 0 ? (
        <div className="no-books">No books found</div>
      ) : (
        <>
          <div className="books-grid">
            {books.map((book) => (
              <div key={book.id} className="book-card">
                <div className="book-icon">📖</div>
                <h3>{book.title}</h3>
                <p className="author">by {book.author}</p>
                <p className="category">{book.category}</p>
                <p className="isbn">ISBN: {book.isbn}</p>
                <div className="availability">
                  <span className={book.available_copies > 0 ? 'available' : 'unavailable'}>
                    {book.available_copies > 0
                      ? `${book.available_copies} available`
                      : 'Not available'}
                  </span>
                </div>
                {user && book.available_copies > 0 && (
                  <button
                    className="btn-borrow"
                    onClick={() => handleBorrow(book.id)}
                  >
                    Borrow Book
                  </button>
                )}
              </div>
            ))}
          </div>

          {pagination.pages > 1 && (
            <div className="pagination">
              <button
                onClick={() => setPage(page - 1)}
                disabled={!pagination.has_prev}
              >
                Previous
              </button>
              <span>
                Page {pagination.page} of {pagination.pages}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={!pagination.has_next}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Books;
