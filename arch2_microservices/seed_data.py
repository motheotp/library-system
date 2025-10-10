#!/usr/bin/env python3
"""
Seed dummy data into arch2_microservices via Gateway API

Usage:
    python3 seed_data.py
"""

import requests
import json
import time

GATEWAY_URL = "http://localhost:8000"

# Sample users data (matching arch1 sample data)
SAMPLE_USERS = [
    {"student_id": "STU001", "name": "John Student", "email": "john@university.edu", "role": "student"},
    {"student_id": "STU002", "name": "Jane Learner", "email": "jane@university.edu", "role": "student"},
    {"student_id": "STU003", "name": "Bob Reader", "email": "bob@university.edu", "role": "student"},
    {"student_id": "STU004", "name": "Alice Scholar", "email": "alice@university.edu", "role": "student"},
    {"student_id": "LIB001", "name": "Library Admin", "email": "admin@library.edu", "role": "admin"},
]

# Sample books data (matching arch1 sample data with category, description, copies)
SAMPLE_BOOKS = [
    {
        "title": "Python Programming",
        "author": "John Doe",
        "isbn": "978-0123456789",
        "category": "Programming",
        "description": "Complete guide to Python programming",
        "total_copies": 3
    },
    {
        "title": "Data Structures and Algorithms",
        "author": "Jane Smith",
        "isbn": "978-0987654321",
        "category": "Computer Science",
        "description": "Fundamental concepts in data structures",
        "total_copies": 2
    },
    {
        "title": "Web Development with Flask",
        "author": "Bob Johnson",
        "isbn": "978-0456789123",
        "category": "Web Development",
        "description": "Building web applications with Flask",
        "total_copies": 4
    },
    {
        "title": "Database Systems",
        "author": "Alice Brown",
        "isbn": "978-0789123456",
        "category": "Database",
        "description": "Introduction to database management systems",
        "total_copies": 2
    },
    {
        "title": "Machine Learning Basics",
        "author": "Charlie Davis",
        "isbn": "978-0321654987",
        "category": "AI",
        "description": "Getting started with machine learning",
        "total_copies": 3
    },
    {
        "title": "React.js Development",
        "author": "Sarah Wilson",
        "isbn": "978-0654987321",
        "category": "Web Development",
        "description": "Modern frontend development with React",
        "total_copies": 2
    },
    {
        "title": "System Design Interview",
        "author": "Alex Xu",
        "isbn": "978-0147258369",
        "category": "Interview Prep",
        "description": "Prepare for system design interviews",
        "total_copies": 1
    },
    {
        "title": "Clean Code",
        "author": "Robert Martin",
        "isbn": "978-0132350884",
        "category": "Software Engineering",
        "description": "Writing clean, maintainable code",
        "total_copies": 2
    },
    {
        "title": "Microservices Patterns",
        "author": "Chris Richardson",
        "isbn": "978-1617294549",
        "category": "Architecture",
        "description": "Designing microservices architecture",
        "total_copies": 2
    },
    {
        "title": "Distributed Systems",
        "author": "Martin Kleppmann",
        "isbn": "978-1449373320",
        "category": "Systems",
        "description": "Designing data-intensive applications",
        "total_copies": 1
    },
]


def check_gateway_health():
    """Check if gateway is running"""
    try:
        response = requests.get(f"{GATEWAY_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Gateway is healthy")
            return True
        else:
            print(f"❌ Gateway returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to gateway: {e}")
        print("Make sure gateway is running: docker-compose up -d")
        return False


def create_users():
    """Create sample users"""
    print("\n📝 Creating users...")
    created_users = []

    for user_data in SAMPLE_USERS:
        try:
            response = requests.post(
                f"{GATEWAY_URL}/users/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in [200, 201]:
                data = response.json()
                created_users.append(data.get("user"))
                print(f"  ✅ Created user: {user_data['name']} ({user_data['email']})")
            else:
                print(f"  ⚠️  Failed to create {user_data['name']}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Error creating {user_data['name']}: {e}")

    print(f"\n✅ Created {len(created_users)} users")
    return created_users


def create_books():
    """Create sample books"""
    print("\n📚 Creating books...")
    created_books = []

    for book_data in SAMPLE_BOOKS:
        try:
            response = requests.post(
                f"{GATEWAY_URL}/books",
                json=book_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in [200, 201]:
                book = response.json()
                created_books.append(book)
                print(f"  ✅ Created book: {book_data['title']} by {book_data['author']}")
            else:
                print(f"  ⚠️  Failed to create '{book_data['title']}': {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Error creating '{book_data['title']}': {e}")

    print(f"\n✅ Created {len(created_books)} books")
    return created_books


def create_sample_borrowings(users, books):
    """Create some sample borrowing records (optional)"""
    if not users or not books:
        print("\n⚠️  Skipping borrowings - need users and books first")
        return []

    print("\n📖 Creating sample borrowings...")
    created_borrowings = []

    # Create a few borrowings
    sample_borrowings = [
        {"user_index": 0, "book_index": 0},  # John borrows Python Programming
        {"user_index": 1, "book_index": 2},  # Jane borrows Web Development
        {"user_index": 2, "book_index": 5},  # Bob borrows React.js
    ]

    for borrowing in sample_borrowings:
        user_idx = borrowing["user_index"]
        book_idx = borrowing["book_index"]

        if user_idx >= len(users) or book_idx >= len(books):
            continue

        user = users[user_idx]
        book = books[book_idx]

        try:
            response = requests.post(
                f"{GATEWAY_URL}/borrow",
                json={
                    "user_id": user["id"],
                    "book_id": book["id"]
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in [200, 201]:
                borrowing_data = response.json()
                created_borrowings.append(borrowing_data)
                print(f"  ✅ {user['name']} borrowed '{book['title']}'")
            else:
                print(f"  ⚠️  Failed to create borrowing: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error creating borrowing: {e}")

    print(f"\n✅ Created {len(created_borrowings)} borrowings")
    return created_borrowings


def verify_data():
    """Verify data was created"""
    print("\n🔍 Verifying data...")

    try:
        # Check books
        response = requests.get(f"{GATEWAY_URL}/books")
        if response.status_code == 200:
            data = response.json()
            book_count = len(data.get("books", []))
            print(f"  ✅ Found {book_count} books in database")
        else:
            print(f"  ⚠️  Failed to fetch books: {response.status_code}")

        # Check stats
        response = requests.get(f"{GATEWAY_URL}/admin/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"  ✅ Stats:")
            print(f"     - Total books: {stats.get('total_books', 0)}")
            print(f"     - Available books: {stats.get('available_books', 0)}")
            print(f"     - Borrowed books: {stats.get('borrowed_books', 0)}")
            print(f"     - Total users: {stats.get('total_users', 0)}")
        else:
            print(f"  ⚠️  Failed to fetch stats: {response.status_code}")

    except Exception as e:
        print(f"  ❌ Error verifying data: {e}")


def main():
    print("=" * 60)
    print("🌱 Seeding Dummy Data into arch2_microservices")
    print("=" * 60)

    # 1. Check gateway health
    if not check_gateway_health():
        print("\n❌ Gateway is not running. Please start services:")
        print("   cd /Users/aashishmaharjan/projects/library-system/arch2_microservices")
        print("   docker-compose up -d")
        return

    # 2. Create users
    users = create_users()
    time.sleep(1)  # Brief pause between operations

    # 3. Create books
    books = create_books()
    time.sleep(1)

    # 4. Create some borrowings (optional)
    borrowings = create_sample_borrowings(users, books)
    time.sleep(1)

    # 5. Verify data
    verify_data()

    print("\n" + "=" * 60)
    print("✅ Dummy data seeding complete!")
    print("=" * 60)
    print("\nYou can now:")
    print("  - View books at: http://localhost:3000")
    print("  - Login with: john@university.edu (password: STU001)")
    print("  - Or register a new user")
    print()


if __name__ == "__main__":
    main()
