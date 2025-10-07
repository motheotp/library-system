import pytest
import json
from models import User

class TestUserManagement:
    """Test suite for User Management functionality"""

    def test_register_user_success(self, client, app_context):
        """Test successful user registration"""
        response = client.post('/api/users/register',
            json={
                'student_id': 'STU001',
                'name': 'John Doe',
                'email': 'john@university.edu',
                'role': 'student'
            })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'
        assert data['user']['student_id'] == 'STU001'
        assert data['user']['name'] == 'John Doe'
        assert data['user']['email'] == 'john@university.edu'
        assert data['user']['role'] == 'student'

    def test_register_user_duplicate_student_id(self, client, app_context, sample_users):
        """Test registration with duplicate student ID"""
        response = client.post('/api/users/register',
            json={
                'student_id': 'STU001',  # Already exists
                'name': 'Different Name',
                'email': 'different@university.edu',
                'role': 'student'
            })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error']

    def test_register_user_duplicate_email(self, client, app_context, sample_users):
        """Test registration with duplicate email"""
        response = client.post('/api/users/register',
            json={
                'student_id': 'STU999',
                'name': 'New User',
                'email': 'john@university.edu',  # Already exists
                'role': 'student'
            })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error']

    def test_register_user_missing_fields(self, client, app_context):
        """Test registration with missing required fields"""
        response = client.post('/api/users/register',
            json={
                'student_id': 'STU001',
                'name': 'John Doe'
                # Missing email
            })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['error']

    def test_register_user_no_data(self, client, app_context):
        """Test registration with no data"""
        response = client.post('/api/users/register', json={})
        print('__________________________ response.data __________________________')
        print(response.data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'No data provided' in data['error']

    def test_register_user_default_role(self, client, app_context):
        """Test registration defaults to student role"""
        response = client.post('/api/users/register',
            json={
                'student_id': 'STU002',
                'name': 'Jane Doe',
                'email': 'jane@university.edu'
                # No role specified
            })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['user']['role'] == 'student'

    def test_get_user_by_id_success(self, client, app_context, sample_users):
        """Test retrieving user by ID"""
        user_id = sample_users[0].id
        response = client.get(f'/api/users/{user_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['student_id'] == 'STU001'
        assert data['user']['name'] == 'John Student'

    def test_get_user_by_id_not_found(self, client, app_context):
        """Test retrieving non-existent user"""
        response = client.get('/api/users/99999')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['error']

    def test_login_user_success(self, client, app_context, sample_users):
        """Test successful user login"""
        response = client.post('/api/users/login',
            json={'student_id': 'STU001'})

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Authentication successful'
        assert data['user']['student_id'] == 'STU001'

    def test_login_user_not_found(self, client, app_context):
        """Test login with non-existent student ID"""
        response = client.post('/api/users/login',
            json={'student_id': 'NONEXISTENT'})

        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'not found' in data['error']

    def test_login_user_missing_student_id(self, client, app_context):
        """Test login without student ID"""
        response = client.post('/api/users/login', json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['error']

    def test_register_librarian(self, client, app_context):
        """Test registering a librarian"""
        response = client.post('/api/users/register',
            json={
                'student_id': 'LIB999',
                'name': 'Head Librarian',
                'email': 'head@library.edu',
                'role': 'librarian'
            })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['user']['role'] == 'librarian'

    def test_user_created_at_timestamp(self, client, app_context):
        """Test that user has created_at timestamp"""
        response = client.post('/api/users/register',
            json={
                'student_id': 'STU003',
                'name': 'Test User',
                'email': 'test@university.edu'
            })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'created_at' in data['user']
        assert data['user']['created_at'] is not None
