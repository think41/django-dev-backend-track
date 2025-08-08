# Module Specification: `users`

**Version:** 1.0

**Author:** Mayur Gowda

**Date:** 2025-08-01

---

## 1. Purpose and Responsibility

The `users` module is the central hub for managing user data and user-related activities. It defines the core `User` model and is responsible for storing profile information, tracking borrowing history, and managing book requests.

### Key Responsibilities:
- User Data Management: Handles the CRUD (Create, Read, Update, Delete) operations for user profiles.
- Profile Management: Allows users to view and update their own profile information.
- Borrowing Records: Maintains records of books requested, borrowed, and returned by users.

---

## 2. Dependencies

- `authentication` module: For securing user-specific endpoints.
- `books` module: To link users with the books they borrow.

---

## 3. Data Models / Schema

### User Model
- `id`: uuid
- `username`: str
- `email`: str
- `password`: str (hashed)
- `role`: str (e.g., `"member"`, `"admin"`)
- `created_at`: datetime
- `updated_at`: datetime

### BookRequest Model
- `id`: uuid
- `user_id`: uuid (foreign key to User)
- `book_id`: uuid (foreign key to Book)
- `status`: str (e.g., `"PENDING"`, `"APPROVED"`, `"REJECTED"`)
- `created_at`: datetime
- `updated_at`: datetime

### BorrowHistory Model
- `id`: uuid
- `user_id`: uuid (foreign key to User)
- `book_id`: uuid (foreign key to Book)
- `borrow_date`: datetime
- `return_date`: datetime (nullable)
- `created_at`: datetime
- `updated_at`: datetime

---

## 4. API Endpoints

- `GET /api/users/me`
  - **Description:** Retrieves the profile of the currently authenticated user.
  - **Response:** `{ "id": "...", "username": "...", "email": "..." }`

- `PUT /api/users/me`
  - **Description:** Updates the profile of the currently authenticated user.
  - **Request Body:** `{ "username": "...", "email": "..." }`
  - **Response:** `{ "id": "...", "username": "...", "email": "..." }`

- `GET /api/users/me/history`
  - **Description:** Retrieves the borrowing history for the currently authenticated user.
  - **Response:** `[ { "book_title": "...", "borrow_date": "...", "return_date": "..." } ]`

- `GET /api/users/me/requests`
  - **Description:** Retrieves all book borrow requests made by the currently authenticated user.
  - **Response:** `[ { "book_title": "...", "status": "...", "requested_at": "..." } ]`

---

## 5. Services and Business Logic

- **UserService:** Manages the core CRUD operations for the `User` model. It ensures data integrity and handles user creation in coordination with the `authentication` module.
- **UserProfileService:** Handles business logic related to user profiles, such as updating user information and retrieving profile data for display.
- **BorrowingRecordService:** Manages the creation and retrieval of `BookRequest` and `BorrowHistory` records. It provides a clear history of a user's interactions with the library's books.

