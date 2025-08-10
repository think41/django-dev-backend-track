# Module Specification: `users`

**Version:** 1.1
**Author:** Mayur Gowda
**Date:** 2025-08-10

---

## 1. Purpose and Responsibility

The `users` module manages user accounts, profiles, and their interactions with books in the library system. It defines the `User` model, as well as models for tracking book requests and borrowing history.

### Key Responsibilities:

* **User Data Management:** Create, update, and store user information securely.
* **Profile Management:** Enable users to view and edit personal details.
* **Book Requests & Borrowing Records:** Track the status of book borrow requests and maintain historical borrowing records.

---

## 2. Dependencies

* **`authentication` module:** Handles secure authentication for user actions.
* **`books` module:** Links `User` records to specific books via borrow requests and history.

---

## 3. Data Models / Schema

### **User Model**

* `id`: `uuid` — Primary key.
* `username`: `str` — Unique username for login and identification.
* `email`: `str` — Unique email address (used for authentication).
* `first_name`: `str` — Optional first name.
* `last_name`: `str` — Optional last name.
* `password`: `str` — Hashed password.
* `role`: `str` — `"Member"` or `"Admin"`.
* `is_approved`: `bool` — Whether the account is approved for borrowing.
* `is_active`: `bool` — Whether the account is active.
* `created_at`: `datetime` — When the user was created.
* `updated_at`: `datetime` — When the user was last updated.

---

### **BookRequest Model**

* `id`: `uuid` — Primary key.
* `user_id`: `uuid` — Foreign key to `User`.
* `book_id`: `uuid` — Foreign key to `Book`.
* `request_date`: `datetime` — When the request was made.
* `borrow_date`: `datetime` — When the book was borrowed (nullable).
* `return_date`: `datetime` — When the book was returned (nullable).
* `status`: `str` — `"PENDING"`, `"APPROVED"`, or `"REJECTED"`.
* `created_at`: `datetime` — When the request record was created.
* `updated_at`: `datetime` — When the request record was last updated.

---

### **BorrowHistory Model**

* `id`: `uuid` — Primary key.
* `user_id`: `uuid` — Foreign key to `User`.
* `book_id`: `uuid` — Foreign key to `Book`.
* `borrow_date`: `datetime` — Date when the book was borrowed.
* `return_date`: `datetime` — Date when the book was returned (nullable).

---

## 4. API Endpoints

* **`GET /api/users/me`**
  Retrieves the profile of the authenticated user.
  **Response:** `{ "id": "...", "username": "...", "email": "...", "first_name": "...", "last_name": "...", "role": "...", "is_approved": true }`

* **`PUT /api/users/me`**
  Updates the authenticated user’s profile.
  **Request Body:** `{ "username": "...", "email": "...", "first_name": "...", "last_name": "..." }`
  **Response:** Updated profile details.

* **`GET /api/users/me/history`**
  Retrieves borrowing history for the authenticated user.
  **Response:** `[ { "book_title": "...", "borrow_date": "...", "return_date": "..." } ]`

* **`GET /api/users/me/requests`**
  Retrieves borrow requests for the authenticated user.
  **Response:** `[ { "book_title": "...", "status": "...", "request_date": "...", "borrow_date": "...", "return_date": "..." } ]`

---

## 5. Services and Business Logic

* **UserService:** Handles CRUD operations for `User` objects, ensuring data validation and secure password handling.
* **UserProfileService:** Manages user profile retrieval and updates.
* **BorrowingRecordService:** Coordinates creation and retrieval of `BookRequest` and `BorrowHistory` records, providing detailed tracking of book borrow cycles.

---

If you want, I can also **write a migration-safe script** to load your CSVs directly into these updated models without errors. That way, the `user_id` / `book_id` values from CSV will correctly link to your database rows.
