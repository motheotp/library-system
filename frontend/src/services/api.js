import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// User APIs
export const userAPI = {
  register: (userData) => api.post('/users/register', userData),
  login: (studentId) => api.post('/users/login', { student_id: studentId }),
  getUser: (userId) => api.get(`/users/${userId}`),
};

// Book APIs
export const bookAPI = {
  getBooks: (params) => api.get('/books', { params }),
  searchBooks: (query) => api.get('/books/search', { params: { q: query } }),
  getBook: (bookId) => api.get(`/books/${bookId}`),
  getPopularBooks: (limit = 10) => api.get('/books/popular', { params: { limit } }),
};

// Borrowing APIs
export const borrowingAPI = {
  borrowBook: (userId, bookId) => api.post('/borrow', { user_id: userId, book_id: bookId }),
  returnBook: (borrowingId) => api.post(`/return/${borrowingId}`),
  getUserBorrowedBooks: (userId) => api.get(`/users/${userId}/borrowed`),
  getOverdueBooks: () => api.get('/overdue'),
};

// Reservation APIs
export const reservationAPI = {
  createReservation: (userId, bookId) => api.post('/reserve', { user_id: userId, book_id: bookId }),
};

// Admin/Statistics APIs
export const adminAPI = {
  getStatistics: () => api.get('/admin/stats'),
};

// Health check
export const healthCheck = () => api.get('/health');

export default api;
