# Library Management System (LMS) Backend

A production-ready Django-based library management system with JWT authentication, role-based permissions, and a comprehensive REST API.

## 🚀 Features

### Core Functionality
- **User Management**: Registration, authentication, and role-based access control
- **Book Inventory**: Complete CRUD operations for book management
- **Borrowing System**: Request, approve, and track book borrowings
- **Admin Dashboard**: Django's built-in admin with custom configurations
- **Search & Filter**: Advanced book search with multiple criteria

### Technical Features
- **JWT Authentication**: Secure token-based authentication with refresh mechanism
- **Role-Based Permissions**: Admin and Member roles with different access levels
- **RESTful API**: Comprehensive REST API with proper HTTP status codes
- **Data Validation**: Robust input validation and error handling
- **Audit Trail**: Borrowing history and user activity tracking
- **Admin Approval**: New user registration requires admin approval

## 🏗️ Architecture

### Project Structure
```
lms/
├── authentication/     # JWT auth endpoints
├── users/             # User management & borrowing
├── books/             # Book inventory management
├── settings.py        # Django configuration
├── urls.py           # Main URL routing
└── manage.py
```

### Database Models
- **User**: Extended AbstractUser with role, status, and borrowing records
- **Book**: Simple book model with inventory tracking

### API Design
- **Authentication**: `/api/auth/` - Registration, login, token management
- **Users**: `/api/users/` - Profile management and borrowing operations
- **Books**: `/api/books/` - Book search and admin management

## 🛠️ Setup Instructions

### Prerequisites
1. **Python 3.10+**
2. **PostgreSQL 13+**
3. **pip** (Python package manager)

### 1. Clone and Navigate
```bash
cd /home/nitin/Desktop/django-dev-backend-track
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: Using Docker (Recommended)
```bash
# Start PostgreSQL using docker-compose
docker-compose up -d
```

#### Option B: Manual PostgreSQL Setup
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE lms;
CREATE USER lms_user WITH PASSWORD 'lms_password';
GRANT ALL PRIVILEGES ON DATABASE lms TO lms_user;
ALTER USER lms_user CREATEDB;
\q
```

### 5. Django Setup
```bash
# Run migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Create initial data (optional but recommended)
python3 manage.py setup_initial_data

# Create a superuser (optional - initial data already creates admin user)
python3 manage.py createsuperuser
```

### 6. Start the Server
```bash
python3 manage.py runserver
```

The API will be available at: `http://localhost:8000/api/`

## 📚 API Documentation

### Authentication Endpoints

#### Register New User
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "new_user",
    "email": "user@example.com",
    "password": "secure_password"
}
```

#### User Login
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "admin",
        "role": "ADMIN",
        "status": "ACTIVE"
    }
}
```

### Book Endpoints

#### Search Books (Public)
```http
GET /api/books/search/?title=great&author=fitzgerald&available=true
```

#### Add Book (Admin Only)
```http
POST /api/books/admin/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "New Book",
    "author": "Author Name",
    "genre": "Fiction",
    "total_copies": 3
}
```

### User/Borrowing Endpoints

#### Request Book Borrowing (Members)
```http
POST /api/users/borrow/request/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "book_id": 1
}
```

#### Approve Borrowing (Admin)
```http
PATCH /api/users/admin/approve-borrow/2/1/
Authorization: Bearer <access_token>
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://lms_user:lms_password@localhost:5433/lms

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=3600  # 1 hour
JWT_REFRESH_TOKEN_LIFETIME=86400  # 1 day
```

### Database Settings
Update `lms/settings.py` if using different database credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',  # Default PostgreSQL port
    }
}
```

## 👥 Default Users (Created by setup_initial_data command)

| Username | Password | Role | Status | Description |
|----------|----------|------|--------|-------------|
| admin | admin123 | ADMIN | ACTIVE | System administrator |
| john_doe | john123 | MEMBER | ACTIVE | Active library member |
| jane_smith | jane123 | MEMBER | ACTIVE | Active library member |
| bob_wilson | bob123 | MEMBER | PENDING | Pending approval |
| mike_johnson | mike123 | MEMBER | SUSPENDED | Suspended account |

## 🔐 User Roles & Permissions

### Admin Users
- Manage all books (CRUD operations)
- Approve/reject user registrations
- View all users and borrowing records
- Approve/reject borrowing requests
- Access Django admin panel at `/admin/`

### Member Users
- Search and view books
- Request book borrowing
- Return borrowed books
- View personal borrowing history
- Update profile information

## 🏥 Health Check & Testing

### API Health Check
```http
GET /api/auth/health/
```

### Manual Testing Workflow
1. **Register a new user**: Use registration endpoint
2. **Login as admin**: Get JWT tokens
3. **Approve user registration**: Use admin endpoints
4. **Add books**: Create book inventory
5. **Login as member**: Test member authentication
6. **Request borrowing**: Test borrowing workflow
7. **Approve borrowing**: Test admin approval
8. **Return book**: Complete the cycle

### Management Commands
```bash
# Setup initial data
python3 manage.py setup_initial_data

# Reset all data and recreate
python3 manage.py setup_initial_data --reset

# Create only users
python3 manage.py setup_initial_data --users-only

# Create only books
python3 manage.py setup_initial_data --books-only
```

## 📊 Admin Panel

Access the Django admin panel at: `http://localhost:8000/admin/`

Features:
- User management with borrowing history visualization
- Book inventory with availability tracking
- Bulk actions for user approval and book management
- Rich filtering and search capabilities
- Custom admin views with statistics

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Restart PostgreSQL
sudo service postgresql restart
```

**2. Migration Issues**
```bash
# Reset migrations (development only)
rm -rf lms/users/migrations/
rm -rf lms/books/migrations/
python3 manage.py makemigrations users
python3 manage.py makemigrations books
python3 manage.py migrate
```

**3. JWT Token Issues**
- Ensure token is included in Authorization header: `Bearer <token>`
- Check token expiration (default: 1 hour)
- Use refresh token to get new access token

**4. Permission Denied**
- Check user role and status
- Ensure user is ACTIVE status for API access
- Verify endpoint permissions match user role

## 🚀 Production Deployment

### Security Checklist
- [ ] Set `DEBUG = False`
- [ ] Use environment variables for secrets
- [ ] Configure proper CORS settings
- [ ] Set up HTTPS
- [ ] Use production database
- [ ] Configure email backend
- [ ] Set up logging
- [ ] Enable security middleware

### Performance Optimization
- [ ] Database indexing
- [ ] Query optimization
- [ ] Caching (Redis/Memcached)
- [ ] Static file serving (nginx/CDN)
- [ ] Connection pooling

## 📄 License

This project is built for educational purposes and follows Django best practices for a production-ready application.
