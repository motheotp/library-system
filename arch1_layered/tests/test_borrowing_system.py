import pytest
import json
from datetime import datetime, timedelta
from models import Book, Borrowing, db

class TestBorrowingSystem:
    """Test suite for Borrowing System functionality"""

    def test_borrow_book_success(self, client, app_context, sample_users, sample_books):
        """Test successful book borrowing"""
        user_id = sample_users[0].id
        book_id = sample_books[0].id
        initial_available = sample_books[0].available_copies

        response = client.post('/api/borrow',
            json={
                'user_id': user_id,
                'book_id': book_id
            })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'successfully' in data['message']
        assert data['borrowing']['user_id'] == user_id
        assert data['borrowing']['book_id'] == book_id
        assert data['borrowing']['returned'] == False

        # Check book availability decreased
        book = Book.query.get(book_id)
        assert book.available_copies == initial_available - 1

    def test_borrow_book_missing_fields(self, client, app_context):
        """Test borrowing without required fields"""
        response = client.post('/api/borrow', json={'user_id': 1})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['error']

    def test_borrow_book_user_not_found(self, client, app_context, sample_books):
        """Test borrowing with non-existent user"""
        response = client.post('/api/borrow',
            json={
                'user_id': 99999,
                'book_id': sample_books[0].id
            })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'not found' in data['error']

    def test_borrow_book_not_found(self, client, app_context, sample_users):
        """Test borrowing non-existent book"""
        response = client.post('/api/borrow',
            json={
                'user_id': sample_users[0].id,
                'book_id': 99999
            })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'not found' in data['error']

    def test_borrow_unavailable_book(self, client, app_context, sample_users, sample_books):
        """Test borrowing a book that's not available"""
        # sample_books[3] has 0 available copies
        response = client.post('/api/borrow',
            json={
                'user_id': sample_users[0].id,
                'book_id': sample_books[3].id
            })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'not available' in data['error']

    def test_borrow_book_already_borrowed(self, client, app_context, sample_users, sample_books):
        """Test borrowing same book twice"""
        user_id = sample_users[0].id
        book_id = sample_books[0].id

        # First borrowing
        client.post('/api/borrow', json={'user_id': user_id, 'book_id': book_id})

        # Second borrowing of same book
        response = client.post('/api/borrow', json={'user_id': user_id, 'book_id': book_id})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already have this book' in data['error']

    def test_borrow_limit_exceeded(self, client, app_context, sample_users, sample_books):
        """Test borrowing more than allowed limit (3 books)"""
        user_id = sample_users[0].id

        # Borrow 3 books (max limit)
        for i in range(3):
            client.post('/api/borrow',
                json={'user_id': user_id, 'book_id': sample_books[i].id})

        # Try to borrow 4th book
        response = client.post('/api/borrow',
            json={'user_id': user_id, 'book_id': sample_books[4].id})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'limit' in data['error'].lower()

    def test_borrow_due_date_set(self, client, app_context, sample_users, sample_books):
        """Test that due date is set correctly (14 days)"""
        response = client.post('/api/borrow',
            json={
                'user_id': sample_users[0].id,
                'book_id': sample_books[0].id
            })

        assert response.status_code == 200
        data = json.loads(response.data)

        borrowed_date = datetime.fromisoformat(data['borrowing']['borrowed_date'].replace('Z', '+00:00'))
        due_date = datetime.fromisoformat(data['borrowing']['due_date'].replace('Z', '+00:00'))

        days_diff = (due_date - borrowed_date).days
        assert days_diff == 14

    def test_return_book_success(self, client, app_context, sample_borrowing, sample_books):
        """Test successful book return"""
        borrowing_id = sample_borrowing.id
        book_id = sample_borrowing.book_id
        book = Book.query.get(book_id)
        initial_available = book.available_copies

        response = client.post(f'/api/return/{borrowing_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'successfully' in data['message']
        assert data['borrowing']['returned'] == True
        assert data['borrowing']['returned_date'] is not None

        # Check book availability increased
        book = Book.query.get(book_id)
        assert book.available_copies == initial_available + 1

    def test_return_book_not_found(self, client, app_context):
        """Test returning non-existent borrowing"""
        response = client.post('/api/return/99999')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'not found' in data['error']

    def test_return_book_already_returned(self, client, app_context, sample_borrowing):
        """Test returning already returned book"""
        borrowing_id = sample_borrowing.id

        # Return once
        client.post(f'/api/return/{borrowing_id}')

        # Try to return again
        response = client.post(f'/api/return/{borrowing_id}')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already returned' in data['error']

    def test_return_overdue_book_calculates_fine(self, client, app_context, overdue_borrowing):
        """Test that returning overdue book calculates fine"""
        borrowing_id = overdue_borrowing.id

        response = client.post(f'/api/return/{borrowing_id}')

        print('__________________________ response.data __________________________')
        print(response.data)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['borrowing']['fine_amount'] > 0
        # 6 days overdue = $6
        assert data['borrowing']['fine_amount'] == 6.0

    def test_return_on_time_no_fine(self, client, app_context, sample_borrowing):
        """Test that returning on time has no fine"""
        borrowing_id = sample_borrowing.id

        response = client.post(f'/api/return/{borrowing_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['borrowing']['fine_amount'] == 0.0

    def test_get_user_borrowed_books(self, client, app_context, sample_borrowing, sample_users):
        """Test getting user's borrowed books"""
        user_id = sample_users[0].id

        response = client.get(f'/api/users/{user_id}/borrowed')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] > 0
        assert data['user_id'] == user_id
        assert len(data['borrowed_books']) > 0
        assert 'book' in data['borrowed_books'][0]
        assert 'borrowing' in data['borrowed_books'][0]

    def test_get_user_borrowed_books_empty(self, client, app_context, sample_users):
        """Test getting borrowed books for user with none"""
        user_id = sample_users[2].id  # User with no borrowings

        response = client.get(f'/api/users/{user_id}/borrowed')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 0
        assert data['borrowed_books'] == []

    def test_get_user_borrowed_books_includes_days_remaining(self, client, app_context, sample_borrowing, sample_users):
        """Test that borrowed books include days remaining"""
        user_id = sample_users[0].id

        response = client.get(f'/api/users/{user_id}/borrowed')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'days_remaining' in data['borrowed_books'][0]

    def test_get_overdue_books(self, client, app_context, overdue_borrowing):
        """Test getting all overdue books"""
        response = client.get('/api/overdue')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] > 0
        assert len(data['overdue_books']) > 0

        # Check overdue book contains all necessary info
        overdue = data['overdue_books'][0]
        assert 'borrowing' in overdue
        assert 'book' in overdue
        assert 'user' in overdue
        assert overdue['borrowing']['is_overdue'] == True

    def test_get_overdue_books_empty(self, client, app_context, sample_borrowing):
        """Test getting overdue books when none exist"""
        response = client.get('/api/overdue')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 0
        assert data['overdue_books'] == []

    def test_borrowing_includes_overdue_status(self, client, app_context, overdue_borrowing, sample_users):
        """Test that borrowing info includes overdue status"""
        user_id = overdue_borrowing.user_id

        response = client.get(f'/api/users/{user_id}/borrowed')

        assert response.status_code == 200
        data = json.loads(response.data)
        borrowing = data['borrowed_books'][0]['borrowing']

        assert 'is_overdue' in borrowing
        assert borrowing['is_overdue'] == True
        assert 'days_overdue' in borrowing
        assert borrowing['days_overdue'] > 0

    def test_multiple_users_can_borrow_different_copies(self, client, app_context, sample_users, sample_books):
        """Test that multiple users can borrow different copies of same book"""
        # Book 0 has 3 copies
        book_id = sample_books[0].id

        # User 1 borrows
        response1 = client.post('/api/borrow',
            json={'user_id': sample_users[0].id, 'book_id': book_id})
        assert response1.status_code == 200

        # User 2 borrows same book
        response2 = client.post('/api/borrow',
            json={'user_id': sample_users[1].id, 'book_id': book_id})
        assert response2.status_code == 200

        # Check only 1 copy left
        book = Book.query.get(book_id)
        assert book.available_copies == 1

    def test_borrow_last_copy_makes_unavailable(self, client, app_context, sample_users, sample_books):
        """Test borrowing last copy makes book unavailable"""
        # Create a book with only 1 copy
        book = Book(
            title="Last Copy Book",
            author="Test Author",
            isbn="978-1111111111",
            category="Test",
            total_copies=1,
            available_copies=1
        )
        db.session.add(book)
        db.session.commit()

        # Borrow the last copy
        response = client.post('/api/borrow',
            json={'user_id': sample_users[0].id, 'book_id': book.id})

        assert response.status_code == 200

        # Try to borrow again - should fail
        response2 = client.post('/api/borrow',
            json={'user_id': sample_users[1].id, 'book_id': book.id})

        assert response2.status_code == 400
        data = json.loads(response2.data)
        assert 'not available' in data['error']

    def test_return_book_makes_available_again(self, client, app_context, sample_users, sample_books):
        """Test that returning book makes it available for others"""
        book_id = sample_books[0].id
        user1_id = sample_users[0].id
        user2_id = sample_users[1].id

        # User 1 borrows
        borrow_response = client.post('/api/borrow',
            json={'user_id': user1_id, 'book_id': book_id})
        borrowing_id = json.loads(borrow_response.data)['borrowing']['id']

        # User 1 returns
        client.post(f'/api/return/{borrowing_id}')

        # User 2 can now borrow
        response = client.post('/api/borrow',
            json={'user_id': user2_id, 'book_id': book_id})

        assert response.status_code == 200
