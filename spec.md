# Library Management System Specification

**Version:** 1.0

**Author:** Mufti Usman

**Date:** 2025-08-01

---

## 1. Purpose and Responsibility

The Library Management System is designed to give library operations by providing a digital platform for managing books, members, and borrowing processes. The system will serve two main user roles: Admins and Members, each with specific permissions.

### Core Responsibilities
- Manage book inventory
- Manage member accounts (registrations and authentication)
- Manage book borrowing and returning process
- Track borrowing history and due dates
- Provide search and filtering capabilities for books


## 2. Dependencies


## 3. Data Models / Schema

### User Model
- id: UUID (primary key)
- email: EmailField (unique)
- username: CharField (unique)
- password: CharField
- role: CharField (choices: 'admin', 'member')
- is_active: BooleanField
- created_at: DateTimeField
- updated_at: DateTimeField

### Book Model
- id: UUID (primary key)
- title: CharField
- author: CharField
- genre: CharField
- quantity: IntegerField
- available_copies: IntegerField
- created_at: DateTimeField
- updated_at: DateTimeField

### BorrowRecord Model
- id: UUID (primary key)
- book: ForeignKey(Book)
- member: ForeignKey(User)
- borrow_date: DateTimeField
- due_date: DateTimeField
- return_date: DateTimeField
- status: CharField (choices: 'PENDING', 'APPROVED', 'REJECTED', 'RETURNED')
- created_at: DateTimeField
- updated_at: DateTimeField


## 4. API Endpoints

### Authentication
- `POST /auth/register/` - Register new member (admin approval required)
- `POST /auth/login/` - Login and get JWT tokens
- `POST /auth/refresh/` - Refresh access token
- `POST /auth/verify/` - Verify token

### Books (Public)
- `GET /books/` - List all books (with search/filter)
- `GET /books/<uuid:pk>/` - Get book details

### Member Endpoints (Requires Member/Admin JWT)
- `POST /borrow/request/` - Request to borrow a book
- `POST /borrow/return/<uuid:pk>/` - Return a borrowed book
- `GET /borrow/history/` - View personal borrowing history

### Admin Only Endpoints (Requires Admin JWT)
- `POST /books/` - Add new book
- `PUT/PATCH /books/<uuid:pk>/` - Update book details
- `DELETE /books/<uuid:pk>/` - Remove book
- `GET /members/` - List all members
- `PATCH /members/<uuid:pk>/approve/` - Approve member registration
- `GET /borrow/` - List all borrow records
- `PATCH /borrow/<uuid:pk>/approve/` - Approve borrow request
- `PATCH /borrow/<uuid:pk>/reject/` - Reject borrow request


## 5. Services and Business Logic

### Authentication Service
- Handle user registration with role assignment
- JWT token generation and validation
- Password encryption and verification
- Token refresh mechanism

### Book Management Service
- CRUD operations for books (Admin)
- Book availability tracking
- Search and filter functionality
- Inventory management

### Borrowing Service
- Handle borrow requests
- Handle book returns
- Calculate due dates
- Track overdue books
- Manage request status (PENDING -> APPROVED/REJECTED -> RETURNED)

### Validation Rules
- Members can only have up to N books borrowed at a time
- Books with 0 available copies cannot be borrowed
- Only admins can approve/reject borrow requests
- Members can only view their own borrowing history
- Book details can only be modified by admins

### Security Considerations
- All API endpoints require authentication
- Role-based access control
- Input validation on all endpoints