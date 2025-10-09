import pytest
import json
from datetime import datetime, timedelta, timezone
from models import Borrowing, Reservation, db

class TestStatisticsAndHealth:
    """Test suite for Statistics and Health Check endpoints"""

    def test_health_check(self, client, app_context):
        """Test health check endpoint"""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data

    def test_health_check_version(self, client, app_context):
        """Test health check returns version"""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['version'] == '1.0.0'

    def test_health_check_timestamp_format(self, client, app_context):
        """Test health check timestamp is ISO format"""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Try parsing timestamp
        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        assert timestamp is not None

    def test_get_statistics_empty_database(self, client, app_context):
        """Test statistics with empty database"""
        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'books' in data
        assert 'users' in data
        assert 'borrowings' in data
        assert 'reservations' in data

        assert data['books']['total'] == 0
        assert data['users']['total'] == 0
        assert data['borrowings']['total'] == 0

    def test_get_statistics_with_data(self, client, app_context, sample_users, sample_books):
        """Test statistics with sample data"""
        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['books']['total'] == len(sample_books)
        assert data['users']['total'] == len(sample_users)

    def test_statistics_books_breakdown(self, client, app_context, sample_books):
        """Test statistics includes book breakdown"""
        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'total' in data['books']
        assert 'available' in data['books']
        assert 'borrowed' in data['books']

        # All books should be counted
        assert data['books']['total'] == 5

    def test_statistics_users_by_role(self, client, app_context, sample_users):
        """Test statistics breaks down users by role"""
        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'students' in data['users']
        assert 'librarians' in data['users']

        # We have 3 students and 1 librarian
        assert data['users']['students'] == 3
        assert data['users']['librarians'] == 1

    def test_statistics_borrowings_breakdown(self, client, app_context, sample_borrowing):
        """Test statistics includes borrowing breakdown"""
        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'total' in data['borrowings']
        assert 'active' in data['borrowings']
        assert 'overdue' in data['borrowings']

        assert data['borrowings']['total'] >= 1
        assert data['borrowings']['active'] >= 1

    def test_statistics_overdue_count(self, client, app_context, overdue_borrowing):
        """Test statistics correctly counts overdue borrowings"""
        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['borrowings']['overdue'] >= 1

    def test_statistics_active_borrowings(self, client, app_context, sample_users, sample_books):
        """Test statistics counts active borrowings correctly"""
        # Create 2 active borrowings
        for i in range(2):
            borrowing = Borrowing(
                user_id=sample_users[i].id,
                book_id=sample_books[i].id,
                borrowed_date=datetime.now(timezone.utc),
                due_date=datetime.now(timezone.utc) + timedelta(days=14),
                returned=False
            )
            db.session.add(borrowing)

        # Create 1 returned borrowing
        returned = Borrowing(
            user_id=sample_users[2].id,
            book_id=sample_books[2].id,
            borrowed_date=datetime.now(timezone.utc) - timedelta(days=10),
            due_date=datetime.now(timezone.utc) + timedelta(days=4),
            returned=True,
            returned_date=datetime.now(timezone.utc)
        )
        db.session.add(returned)
        db.session.commit()

        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['borrowings']['total'] == 3
        assert data['borrowings']['active'] == 2

    def test_statistics_active_reservations(self, client, app_context, sample_reservation):
        """Test statistics includes active reservations"""
        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'reservations' in data
        assert 'active' in data['reservations']
        assert data['reservations']['active'] >= 1

    def test_statistics_reservation_count(self, client, app_context, sample_users, sample_books):
        """Test statistics counts reservations correctly"""
        # Create 2 active reservations
        for i in range(2):
            reservation = Reservation(
                user_id=sample_users[i].id,
                book_id=sample_books[3].id,
                reserved_date=datetime.now(timezone.utc),
                status='active',
                priority=i + 1
            )
            db.session.add(reservation)

        # Create 1 fulfilled reservation
        fulfilled = Reservation(
            user_id=sample_users[2].id,
            book_id=sample_books[3].id,
            reserved_date=datetime.now(timezone.utc) - timedelta(days=5),
            status='fulfilled',
            priority=3
        )
        db.session.add(fulfilled)
        db.session.commit()

        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Only active reservations should be counted
        assert data['reservations']['active'] == 2

    def test_statistics_timestamp(self, client, app_context):
        """Test statistics includes generation timestamp"""
        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'generated_at' in data
        timestamp = datetime.fromisoformat(data['generated_at'].replace('Z', '+00:00'))
        assert timestamp is not None

    def test_statistics_available_books_count(self, client, app_context, sample_books):
        """Test statistics counts available books correctly"""
        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        # 4 out of 5 books have available copies
        assert data['books']['available'] == 4

    def test_statistics_borrowed_books_count(self, client, app_context, sample_users, sample_books):
        """Test statistics counts borrowed books correctly"""
        # Borrow from book that has 3 copies
        borrowing = Borrowing(
            user_id=sample_users[0].id,
            book_id=sample_books[0].id,
            borrowed_date=datetime.now(timezone.utc),
            due_date=datetime.now(timezone.utc) + timedelta(days=14),
            returned=False
        )
        sample_books[0].available_copies -= 1

        db.session.add(borrowing)
        db.session.commit()

        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Books with available_copies < total_copies
        assert data['books']['borrowed'] >= 1

    def test_statistics_json_structure(self, client, app_context, sample_users, sample_books):
        """Test statistics response has correct JSON structure"""
        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Check main structure
        assert isinstance(data['books'], dict)
        assert isinstance(data['users'], dict)
        assert isinstance(data['borrowings'], dict)
        assert isinstance(data['reservations'], dict)

        # Check all values are integers
        assert isinstance(data['books']['total'], int)
        assert isinstance(data['users']['total'], int)
        assert isinstance(data['borrowings']['total'], int)

    def test_statistics_source_indicator(self, client, app_context):
        """Test statistics includes source indicator (cache/database)"""
        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Should have source indicator
        assert 'source' in data
        assert data['source'] in ['cache', 'database']

    def test_health_check_no_auth_required(self, client, app_context):
        """Test health check endpoint doesn't require authentication"""
        response = client.get('/api/health')

        # Should be accessible without any auth
        assert response.status_code == 200

    def test_statistics_comprehensive_data(self, client, app_context, sample_users, sample_books, sample_borrowing, sample_reservation):
        """Test statistics with all types of data present"""
        response = client.get('/api/admin/stats')

        assert response.status_code == 200
        data = json.loads(response.data)

        # All sections should have data
        assert data['books']['total'] > 0
        assert data['users']['total'] > 0
        assert data['borrowings']['total'] > 0
        assert data['reservations']['active'] > 0
