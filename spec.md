# Library Management System - Module Specifications

**Version:** 1.0

**Author:** Shubham kamboj

**Date:** 2025-08-01

---
Library Management System Spec Doc.
---

## Module: `accounts`

### 1. Purpose and Responsibility
Handles user authentication, registration, and management. (for both admin and user)

### 2. Dependencies
- Django
- JWT

### 3. Data Models / Schema
**`User` (Custom User Model)**
- `id`: UUID (Primary Key)
- `username`: String
- `password`: Hashed String
- `email`: EmailField
- `first_name`: String
- `last_name`: String
- `role`: ENUM ('admin', 'user')

### 4. API Endpoints
- `POST /api/accounts/register/`: Allows new users to register.
- `POST /api/accounts/login/`: Authenticates a user and returns JWT access token.
- `GET /api/accounts/users/`: (Admin only) Retrieves a list of all users.

### 5. Services and Business Logic
- **User Registration:** Creates a new user.
- **User Login:** Validates credentials and generates JWTs containing `user_id`, `role`.

---

## Module: `books`

### 1. Purpose and Responsibility
Manages the library's book inventory. It allows admins to perform CRUD operations on books, and allows all users


### 2. Data Models / Schema
**`Book`**
- `id`: UUID (Primary Key)
- `title`: String
- `author`: String
- `quantity`: Integer (Number of copies available)

### 3. API Endpoints
- `GET /api/books/`: Lists all available books with basic details(total books). Supports searching by title & author.
- `POST /api/add/book/`: (Admin only) Adds a new book to the inventory.
- `GET /api/books/{book_id}/`: Retrieves detailed information for a single book.
- `PUT /api/books/{book_id}/`: (Admin only) Updates the details of an existing book.
- `DELETE /api/books/{book_id}/`: (Admin only) Removes a book from the inventory.

### 4. Services and Business Logic
- **Book Management (CRUD):** Provides full create, read, update, and delete functionality for books to admins.
- **Book Search** 

---

## Module: `records`

### 1. Purpose and Responsibility
Manages the process of borrowing and returning books. It handles borrow requests, approvals, rejections, and tracks the history of borrowed books for each member.


### 2. Data Models / Schema
**`BorrowRecord`**
- `id`: UUID (Primary Key)
- `user`: ForeignKey to USER_ID
- `book`: ForeignKey to [BOOKS_ID]
- `borrow_date`: DateTime
- `return_date`: DateTime
- `status`: ENUM ('PENDING', 'APPROVED', 'REJECTED', 'RETURNED')

### 3. API Endpoints
- `POST /api/records/borrow/{book_id}`: (Member only) Allows a member to request to borrow a book. Creates a `BorrowRecord` with 'PENDING' status.
- `POST /api/records/return/{book_id}`: (Member only) Allows a member to return a book. Updates the `status` to 'RETURNED' and sets the `return_date`.
- `GET /api/records/`: (Admin only) Lists all borrow records, with filtering options for status.
- `POST /api/records/{}/approve/`: (Admin only) Approves a 'PENDING' borrow request. Changes status to 'APPROVED'.
- `POST /api/records/{}/reject/`: (Admin only) Rejects a 'PENDING' borrow request. Changes status to 'REJECTED'.

### 4. Services and Business Logic
- **Borrow Request:** all details
- **Borrow Approval/Rejection:** Admins - If approved --book if reject nothing.
- **Book Return:** When a book is returned, ++book.
