import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
import json
from models import Book, Borrowing
from datetime import datetime, timedelta, timezone

class TestBookManagement:
    """Test suite for Book Management functionality"""

    def test_get_books_default_pagination(self, client, app_context, sample_books):
        """Test getting books with default pagination"""
        response = client.get('/api/books')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'books' in data
        assert 'pagination' in data
        assert len(data['books']) > 0
        assert data['pagination']['page'] == 1

    def test_get_books_with_pagination(self, client, app_context, sample_books):
        """Test getting books with custom pagination"""
        response = client.get('/api/books?page=1&limit=2')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['books']) <= 2
        assert data['pagination']['page'] == 1
        assert 'total' in data['pagination']

    def test_get_books_filter_by_category(self, client, app_context, sample_books):
        """Test filtering books by category"""
        response = client.get('/api/books?category=Programming')

        assert response.status_code == 200
        data = json.loads(response.data)
        for book in data['books']:
            assert book['category'] == 'Programming'

    def test_get_books_only_available(self, client, app_context, sample_books):
        """Test that only available books are returned"""
        response = client.get('/api/books')

        assert response.status_code == 200
        data = json.loads(response.data)
        # Book with isbn 978-0789123456 has 0 available copies
        book_isbns = [book['isbn'] for book in data['books']]
        assert '978-0789123456' not in book_isbns

    def test_get_books_empty_result(self, client, app_context):
        """Test getting books when none exist"""
        response = client.get('/api/books')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['books'] == []

    def test_search_books_by_title(self, client, app_context, sample_books):
        """Test searching books by title"""
        response = client.get('/api/books/search?q=Python')
        print('__________________________ response.data __________________________')
        print(response.data)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['query'] == 'Python'
        assert data['count'] > 0
        assert any('Python' in book['title'] for book in data['books'])

    def test_search_books_by_author(self, client, app_context, sample_books):
        """Test searching books by author"""
        response = client.get('/api/books/search?q=John Doe')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] > 0
        assert any('John Doe' in book['author'] for book in data['books'])

    def test_search_books_case_insensitive(self, client, app_context, sample_books):
        """Test that search is case insensitive"""
        response_lower = client.get('/api/books/search?q=python')
        response_upper = client.get('/api/books/search?q=PYTHON')

        data_lower = json.loads(response_lower.data)
        data_upper = json.loads(response_upper.data)

        assert data_lower['count'] == data_upper['count']

    def test_search_books_no_query(self, client, app_context, sample_books):
        """Test search without query parameter"""
        response = client.get('/api/books/search')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['error']

    def test_search_books_empty_query(self, client, app_context, sample_books):
        """Test search with empty query"""
        response = client.get('/api/books/search?q=')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['error']

    def test_search_books_no_results(self, client, app_context, sample_books):
        """Test search with no matching results"""
        response = client.get('/api/books/search?q=NonexistentBook12345')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 0
        assert data['books'] == []

    def test_get_book_by_id_success(self, client, app_context, sample_books):
        """Test getting a book by ID"""
        book_id = sample_books[0].id
        response = client.get(f'/api/books/{book_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['book']['title'] == 'Python Programming'
        assert data['book']['author'] == 'John Doe'
        assert data['book']['isbn'] == '978-0123456789'

    def test_get_book_by_id_not_found(self, client, app_context):
        """Test getting non-existent book"""
        response = client.get('/api/books/99999')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['error']

    def test_get_book_details_include_availability(self, client, app_context, sample_books):
        """Test that book details include availability status"""
        book_id = sample_books[0].id
        response = client.get(f'/api/books/{book_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'available_copies' in data['book']
        assert 'total_copies' in data['book']
        assert 'is_available' in data['book']

    def test_get_popular_books(self, client, app_context, sample_books, sample_users):
        """Test getting popular books based on borrow count"""
        # Create some borrowings
        borrowing1 = Borrowing(
            user_id=sample_users[0].id,
            book_id=sample_books[0].id,
            borrowed_date=datetime.now(timezone.utc),
            due_date=datetime.now(timezone.utc) + timedelta(days=14),
            returned=True,
            returned_date=datetime.now(timezone.utc)
        )
        borrowing2 = Borrowing(
            user_id=sample_users[1].id,
            book_id=sample_books[0].id,
            borrowed_date=datetime.now(timezone.utc),
            due_date=datetime.now(timezone.utc) + timedelta(days=14),
            returned=True,
            returned_date=datetime.now(timezone.utc)
        )

        from models import db
        db.session.add(borrowing1)
        db.session.add(borrowing2)
        db.session.commit()

        response = client.get('/api/books/popular')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'popular_books' in data
        assert len(data['popular_books']) > 0
        assert 'borrow_count' in data['popular_books'][0]

    def test_get_popular_books_with_limit(self, client, app_context, sample_books, sample_users):
        """Test getting popular books with custom limit"""
        # Create borrowings
        from models import db
        for i in range(3):
            borrowing = Borrowing(
                user_id=sample_users[0].id,
                book_id=sample_books[i].id,
                borrowed_date=datetime.now(timezone.utc),
                due_date=datetime.now(timezone.utc) + timedelta(days=14),
                returned=True
            )
            db.session.add(borrowing)
        db.session.commit()

        response = client.get('/api/books/popular?limit=2')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['popular_books']) <= 2

    def test_get_popular_books_empty(self, client, app_context, sample_books):
        """Test getting popular books when no borrowings exist"""
        response = client.get('/api/books/popular')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['popular_books'] == []

    def test_book_to_dict_format(self, client, app_context, sample_books):
        """Test that book dict contains all expected fields"""
        book_id = sample_books[0].id
        response = client.get(f'/api/books/{book_id}')

        data = json.loads(response.data)
        book = data['book']

        expected_fields = [
            'id', 'title', 'author', 'isbn', 'category',
            'description', 'total_copies', 'available_copies',
            'is_available', 'created_at', 'updated_at'
        ]

        for field in expected_fields:
            assert field in book

    def test_pagination_metadata(self, client, app_context, sample_books):
        """Test pagination metadata is correct"""
        response = client.get('/api/books?page=1&limit=2')

        assert response.status_code == 200
        data = json.loads(response.data)
        pagination = data['pagination']

        assert 'page' in pagination
        assert 'pages' in pagination
        assert 'total' in pagination
        assert 'has_next' in pagination
        assert 'has_prev' in pagination
        assert pagination['has_prev'] == False  # First page

    def test_search_partial_match(self, client, app_context, sample_books):
        """Test search works with partial matches"""
        response = client.get('/api/books/search?q=Pyth')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] > 0
        assert any('Python' in book['title'] for book in data['books'])
