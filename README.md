<<<<<<< HEAD
# Student Course Management API

A Flask-based REST API for managing students and courses with JWT authentication.

## Features

- JWT Authentication
- User roles (admin/student)
- Course management
- Student management
- SQLite database

## Setup

1. Clone the repository
```bash
git clone <your-repo-url>
cd student_course_backend
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize the database
```bash
python app.py
```

## API Endpoints

### Authentication
- POST /auth/register - Register a new user
- POST /auth/login - Login and get JWT token

### Courses
- GET /courses - Get all courses

### Students
- GET /students - Get all students (admin) or own details (student)
- POST /students - Add a new student (admin only)
- PUT /students/<id> - Update student details (admin only)
- DELETE /students/<id> - Delete a student (admin only)
- GET /students/by-course/<code> - Get students by course code

## License

MIT
=======
# student-management
>>>>>>> 2f2a7e8739223526e9e5fb051f281c1f2e68fc9d
