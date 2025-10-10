-- Insert sample users
INSERT INTO users (student_id, name, email, role) VALUES 
('STU001', 'John Student', 'john@university.edu', 'student'),
('STU002', 'Jane Learner', 'jane@university.edu', 'student'),
('STU003', 'Bob Reader', 'bob@university.edu', 'student'),
('STU004', 'Alice Scholar', 'alice@university.edu', 'student'),
('LIB001', 'Library Admin', 'admin@library.edu', 'librarian')
ON CONFLICT (student_id) DO NOTHING;

-- Insert sample books
INSERT INTO books (title, author, isbn, category, description, total_copies, available_copies) VALUES 
('Python Programming', 'John Doe', '978-0123456789', 'Programming', 'Complete guide to Python programming', 3, 3),
('Data Structures and Algorithms', 'Jane Smith', '978-0987654321', 'Computer Science', 'Fundamental concepts in data structures', 2, 2),
('Web Development with Flask', 'Bob Johnson', '978-0456789123', 'Web Development', 'Building web applications with Flask', 4, 4),
('Database Systems', 'Alice Brown', '978-0789123456', 'Database', 'Introduction to database management systems', 2, 2),
('Machine Learning Basics', 'Charlie Davis', '978-0321654987', 'AI', 'Getting started with machine learning', 3, 3),
('React.js Development', 'Sarah Wilson', '978-0654987321', 'Web Development', 'Modern frontend development with React', 2, 2),
('System Design Interview', 'Alex Xu', '978-0147258369', 'Interview Prep', 'Prepare for system design interviews', 1, 1),
('Clean Code', 'Robert Martin', '978-0132350884', 'Software Engineering', 'Writing clean, maintainable code', 2, 2),
('Microservices Patterns', 'Chris Richardson', '978-1617294549', 'Architecture', 'Designing microservices architecture', 2, 2),
('Distributed Systems', 'Martin Kleppmann', '978-1449373320', 'Systems', 'Designing data-intensive applications', 1, 1)
ON CONFLICT (isbn) DO NOTHING;