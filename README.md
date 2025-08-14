# Library Management System (LMS)

A Django REST API application for managing a library's book catalog and borrowing system.

## Features

### User Management
- User registration with admin approval
- JWT-based authentication
- Role-based access control (Admin/Member)
- User activation by admins

### Book Management
- Complete CRUD operations for books
- Search functionality by title, author, or genre
- Book quantity tracking
- Admin-only book management

### Borrowing System
- Members can request to borrow books
- Admin approval workflow for borrow requests
- Book return functionality
- Status tracking (PENDING, APPROVED, REJECTED, RETURNED)
- Automatic inventory management

## Architecture

The application follows Django best practices with:
- **Models**: Data layer with User, Book, and BorrowRecord models
- **Serializers**: Data validation and serialization
- **Services**: Business logic layer for complex operations
- **Views**: API endpoints with proper permissions
- **Permissions**: Custom permission classes for role-based access

## API Endpoints

### Authentication Endpoints
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login (returns JWT tokens)

### User Management (Admin only)
- `GET /api/users/admin/users/` - List all users (filterable by active status)
- `PATCH /api/users/admin/users/{id}/approve/` - Approve user registration

### Book Management
- `GET /api/books/` - List all books (supports search)
- `POST /api/books/` - Create new book (Admin only)
- `GET /api/books/{id}/` - Get book details
- `PUT /api/books/{id}/` - Update book (Admin only)
- `DELETE /api/books/{id}/` - Delete book (Admin only)

### Borrowing System
- `POST /api/books/borrow/` - Request to borrow a book
- `POST /api/books/return/` - Return a borrowed book

### Admin Borrowing Management
- `GET /api/books/admin/borrow/` - List all borrow records (filterable by status)
- `PATCH /api/books/admin/borrow/{id}/approve/` - Approve borrow request
- `PATCH /api/books/admin/borrow/{id}/reject/` - Reject borrow request

## Data Models

### User Model
- Extends Django's AbstractUser
- Additional fields: `role` (admin/member), custom `is_active` default

### Book Model
- Fields: `title`, `author`, `genre`, `quantity`, timestamps

### BorrowRecord Model
- Tracks borrowing transactions
- Fields: `user`, `book`, `status`, `borrow_date`, `return_date`, timestamps

## Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL
- Redis (for Celery)
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-dev-backend-track
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database**
   - Update database settings in `lms/settings.py`
   - Create PostgreSQL database named `lms`

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create initial data**
   ```bash
   python manage.py setup_initial_data
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

### Docker Setup

1. **Build and start services**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations (in another terminal)**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py setup_initial_data
   ```

## Default Users

After running `setup_initial_data`:
- **Admin**: username: `admin`, password: `admin123`
- **Member**: username: `member1`, password: `member123`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Login** to get tokens:
   ```bash
   POST /api/users/login/
   {
     "username": "admin",
     "password": "admin123"
   }
   ```

2. **Include token** in requests:
   ```bash
   Authorization: Bearer <access_token>
   ```

## Usage Examples

### Register a new user
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "newpass123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### List books
```bash
curl -X GET http://localhost:8000/api/books/ \
  -H "Authorization: Bearer <access_token>"
```

### Search books
```bash
curl -X GET "http://localhost:8000/api/books/?search=python" \
  -H "Authorization: Bearer <access_token>"
```

### Request to borrow a book
```bash
curl -X POST http://localhost:8000/api/books/borrow/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1}'
```

### Approve borrow request (Admin only)
```bash
curl -X PATCH http://localhost:8000/api/books/admin/borrow/1/approve/ \
  -H "Authorization: Bearer <admin_access_token>"
```

## Business Rules

### User Registration
- New users are created as inactive
- Admin approval required to activate accounts
- Default role is 'member'

### Book Borrowing
- Users can only request books that are available (quantity > 0)
- Users cannot have multiple pending/approved requests for the same book
- Admin approval required for all borrow requests
- Book quantity decreases when request is approved
- Book quantity increases when book is returned

### Permissions
- **Public**: Registration, Login
- **Authenticated Users**: View books, request borrowing, return books
- **Admin Only**: User management, book CRUD, borrow request management

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
The project follows Django and PEP 8 conventions.

### Project Structure
```
django-dev-backend-track/
├── lms/                    # Main Django project
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── users/                  # User management app
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── services.py
│   └── ...
├── books/                  # Book management app
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── services.py
│   └── ...
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Technologies Used

- **Backend**: Django 5.2.1, Django REST Framework 3.15.2
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **Containerization**: Docker & Docker Compose

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is for educational purposes.