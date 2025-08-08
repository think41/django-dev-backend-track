# Module Specification: `admin`

**Version:** 1.0

**Author:** Mayur Gowda

**Date:** 2025-08-01

---

## 1. Purpose and Responsibility

The `admin` module provides administrative functionalities for the library management system. It defines a special type of user, the "admin," who has elevated privileges to manage the library's resources, including books and user memberships.

### Key Responsibilities:
- User Management: Approve or reject new member registrations.
- Book Management: Add, update, and remove books from the library's collection.
- Borrow Request Management: Approve or reject requests from users to borrow books.
- Record Monitoring: View and filter all borrowing records to monitor the status of books (e.g., PENDING, APPROVED, RETURNED).

---

## 2. Dependencies

- `users` module: For the base user model and authentication.
- `books` module: For managing the book inventory.

---

## 3. Data Models / Schema

The `admin` module does not introduce new data models. It utilizes the `User` model from the `users` module, where the `role` attribute is set to `"admin"` to grant administrative privileges.

**User Model (from `users` module):**
- `id`: uuid
- `username`: str
- `email`: str
- `password`: str
- `role`: str (e.g., `"member"`, `"admin"`)
- `created_at`: datetime
- `updated_at`: datetime

---

## 4. API Endpoints

### Book Management
- `POST /api/admin/books`
  - **Description:** Adds a new book to the library.
  - **Request Body:** `{ "title": "...", "author": "...", "genre": "..." }`
  - **Response:** `{ "id": "...", "title": "...", ... }`

- `PUT /api/admin/books/<book_id>`
  - **Description:** Updates an existing book's details.
  - **Request Body:** `{ "title": "...", "author": "...", ... }`
  - **Response:** `{ "id": "...", "title": "...", ... }`

- `DELETE /api/admin/books/<book_id>`
  - **Description:** Removes a book from the library.
  - **Response:** `204 No Content`

### User Management
- `GET /api/admin/users`
  - **Description:** Retrieves a list of all users.
  - **Response:** `[ { "id": "...", "username": "...", ... } ]`

- `POST /api/admin/users/approve/<member_id>`
  - **Description:** Approves a new member's registration.
  - **Response:** `{ "message": "Member approved successfully" }`

### Borrow Request Management
- `GET /api/admin/requests`
  - **Description:** Retrieves all borrow requests. Can be filtered by status (e.g., `?status=PENDING`).
  - **Response:** `[ { "id": "...", "user_id": "...", "book_id": "...", "status": "..." } ]`

- `POST /api/admin/requests/<request_id>/approve`
  - **Description:** Approves a borrow request.
  - **Response:** `{ "message": "Request approved" }`

- `POST /api/admin/requests/<request_id>/reject`
  - **Description:** Rejects a borrow request.
  - **Response:** `{ "message": "Request rejected" }`

---

## 5. Services and Business Logic

- **AdminAuthService:** Middleware to verify that the user has `admin` privileges before allowing access to protected endpoints.
- **BookManagementService:** Contains the logic for creating, updating, and deleting books. It should handle validation and interact with the `books` module.
- **UserManagementService:** Manages user-related administrative tasks, such as approving new members.
- **RequestManagementService:** Handles the logic for approving and rejecting borrow requests, updating the status of the request and the book accordingly.

