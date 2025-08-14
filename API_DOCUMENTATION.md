# Library Management System - API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints (except registration and login) require JWT authentication.

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## Authentication Endpoints

### Register User
Creates a new user account (requires admin approval).

**Endpoint:** `POST /users/register/`

**Permissions:** Public

**Request Body:**
```json
{
  "username": "string",
  "email": "string", 
  "password": "string"
}
```

**Success Response (201):**
```json
{
  "message": "Registration successful. Your account is pending approval from an administrator."
}
```

**Error Response (400):**
```json
{
  "username": ["This field is required."],
  "email": ["Enter a valid email address."]
}
```

### User Login
Authenticates user and returns JWT tokens.

**Endpoint:** `POST /users/login/`

**Permissions:** Public

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Success Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Response (401):**
```json
{
  "non_field_errors": ["Invalid credentials"]
}
```

---

## User Management (Admin Only)

### List Users
Retrieves all users in the system.

**Endpoint:** `GET /users/admin/users/`

**Permissions:** Admin only

**Query Parameters:**
- `is_active` (optional): Filter by active status (`true`/`false`)

**Success Response (200):**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@library.com",
    "role": "admin",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "username": "member1",
    "email": "member1@library.com", 
    "role": "member",
    "is_active": false,
    "date_joined": "2024-01-02T00:00:00Z"
  }
]
```

### Approve User
Activates a user account.

**Endpoint:** `PATCH /users/admin/users/{user_id}/approve/`

**Permissions:** Admin only

**Success Response (200):**
```json
{
  "message": "User account activated successfully."
}
```

**Error Response (404):**
```json
{
  "error": "User not found"
}
```

---

## Book Management

### List/Search Books
Retrieves all books with optional search functionality.

**Endpoint:** `GET /books/`

**Permissions:** Authenticated users

**Query Parameters:**
- `search` (optional): Search by title, author, or genre

**Success Response (200):**
```json
[
  {
    "id": 1,
    "title": "To Kill a Mockingbird",
    "author": "Harper Lee",
    "genre": "Fiction",
    "quantity": 3,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "title": "1984",
    "author": "George Orwell",
    "genre": "Dystopian Fiction",
    "quantity": 2,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### Create Book
Creates a new book in the catalog.

**Endpoint:** `POST /books/`

**Permissions:** Admin only

**Request Body:**
```json
{
  "title": "string",
  "author": "string",
  "genre": "string",
  "quantity": "integer"
}
```

**Success Response (201):**
```json
{
  "id": 3,
  "title": "New Book",
  "author": "Author Name",
  "genre": "Genre",
  "quantity": 5,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get Book Details
Retrieves a single book by ID.

**Endpoint:** `GET /books/{book_id}/`

**Permissions:** Authenticated users

**Success Response (200):**
```json
{
  "id": 1,
  "title": "To Kill a Mockingbird",
  "author": "Harper Lee",
  "genre": "Fiction",
  "quantity": 3,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Response (404):**
```json
{
  "detail": "Not found."
}
```

### Update Book
Updates all fields of a book.

**Endpoint:** `PUT /books/{book_id}/`

**Permissions:** Admin only

**Request Body:**
```json
{
  "title": "string",
  "author": "string", 
  "genre": "string",
  "quantity": "integer"
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "title": "Updated Title",
  "author": "Updated Author",
  "genre": "Updated Genre",
  "quantity": 10,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Delete Book
Removes a book from the catalog.

**Endpoint:** `DELETE /books/{book_id}/`

**Permissions:** Admin only

**Success Response (204):**
No content

---

## Borrowing System

### Request to Borrow Book
Submits a request to borrow a book.

**Endpoint:** `POST /books/borrow/`

**Permissions:** Authenticated users

**Request Body:**
```json
{
  "book_id": "integer"
}
```

**Success Response (201):**
```json
{
  "message": "Borrow request submitted successfully. Waiting for admin approval."
}
```

**Error Response (400):**
```json
{
  "error": "Book is not available"
}
```

**Error Response (400):**
```json
{
  "error": "You already have an outstanding request for this book"
}
```

### Return Book
Returns a borrowed book.

**Endpoint:** `POST /books/return/`

**Permissions:** Authenticated users

**Request Body:**
```json
{
  "borrow_record_id": "integer"
}
```

**Success Response (200):**
```json
{
  "message": "Book returned successfully."
}
```

**Error Response (400):**
```json
{
  "error": "This record does not belong to you"
}
```

**Error Response (400):**
```json
{
  "error": "Only approved records can be returned"
}
```

---

## Admin Borrowing Management

### List Borrow Records
Retrieves all borrow records with optional status filtering.

**Endpoint:** `GET /books/admin/borrow/`

**Permissions:** Admin only

**Query Parameters:**
- `status` (optional): Filter by status (`PENDING`, `APPROVED`, `REJECTED`, `RETURNED`)

**Success Response (200):**
```json
[
  {
    "id": 1,
    "user": {
      "id": 2,
      "username": "member1",
      "email": "member1@library.com",
      "role": "member",
      "is_active": true,
      "date_joined": "2024-01-02T00:00:00Z"
    },
    "book": {
      "id": 1,
      "title": "To Kill a Mockingbird",
      "author": "Harper Lee",
      "genre": "Fiction",
      "quantity": 2,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    "borrow_date": "2024-01-03",
    "return_date": null,
    "status": "APPROVED",
    "created_at": "2024-01-03T00:00:00Z",
    "updated_at": "2024-01-03T00:00:00Z"
  }
]
```

### Approve Borrow Request
Approves a pending borrow request.

**Endpoint:** `PATCH /books/admin/borrow/{record_id}/approve/`

**Permissions:** Admin only

**Success Response (200):**
```json
{
  "message": "Borrow request approved."
}
```

**Error Response (400):**
```json
{
  "error": "Only pending requests can be approved"
}
```

**Error Response (400):**
```json
{
  "error": "Book is not available"
}
```

### Reject Borrow Request
Rejects a pending borrow request.

**Endpoint:** `PATCH /books/admin/borrow/{record_id}/reject/`

**Permissions:** Admin only

**Success Response (200):**
```json
{
  "message": "Borrow request rejected."
}
```

**Error Response (400):**
```json
{
  "error": "Only pending requests can be rejected"
}
```

---

## Status Codes

| Code | Description |
|------|-------------|
| 200  | OK - Request successful |
| 201  | Created - Resource created successfully |
| 204  | No Content - Request successful, no content returned |
| 400  | Bad Request - Invalid request data |
| 401  | Unauthorized - Authentication required |
| 403  | Forbidden - Permission denied |
| 404  | Not Found - Resource not found |
| 500  | Internal Server Error - Server error |

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": "Error message description"
}
```

Or for field-specific validation errors:

```json
{
  "field_name": ["Field-specific error message"],
  "another_field": ["Another error message"]
}
```

---

## Rate Limiting

Currently no rate limiting is implemented, but it's recommended for production use.

---

## Pagination

Currently, pagination is not implemented for list endpoints. All results are returned in a single response. For production use, consider implementing pagination for better performance. 