# Module Specification: `books`

**Version:** 1.0

**Author:** Mayur Gowda

**Date:** 2025-08-01

---

## 1. Purpose and Responsibility

The `books` module is responsible for managing the library's collection of books. It handles the data model for books and provides functionalities for users to search for books and for admins to manage the inventory.

### Key Responsibilities:
- Book Inventory: Manages the creation, retrieval, updating, and deletion of book records.
- Book Search: Provides a public-facing search functionality for users to find books by title, author, or genre.
- Availability Tracking: Keeps track of the number of available copies for each book.

---

## 2. Dependencies

- `users` module: To link borrowing activities to specific users.

---

## 3. Data Models / Schema

### Book Model
- `id`: uuid
- `title`: str
- `author`: str
- `genre`: str
- `publication_year`: int
- `available_copies`: int
- `summary`: str
- `created_at`: datetime
- `updated_at`: datetime

---

## 4. API Endpoints

### Public Endpoints
- `GET /api/books`
  - **Description:** Searches for books. Users can filter by title, author, or genre.
  - **Query Parameters:** `?title=...`, `?author=...`, `?genre=...`
  - **Response:** `[ { "id": "...", "title": "...", "author": "...", "available_copies": ... } ]`

- `GET /api/books/<book_id>`
  - **Description:** Retrieves the details of a single book.
  - **Response:** `{ "id": "...", "title": "...", "summary": "...", ... }`

### User-Specific Endpoints (Requires Authentication)
- `POST /api/books/<book_id>/borrow`
  - **Description:** Allows a logged-in user to request to borrow a book.
  - **Response:** `{ "message": "Borrow request submitted successfully. Waiting for approval." }`

- `POST /api/books/<book_id>/return`
  - **Description:** Allows a logged-in user to return a borrowed book.
  - **Response:** `{ "message": "Book returned successfully." }`

- `GET /api/users/me/history`
  - **Description:** Retrieves the borrowing history for the currently authenticated user.
  - **Response:** `[ { "book_id": "...", "title": "...", "borrow_date": "...", "return_date": "..." } ]`

---

## 5. Services and Business Logic

- **BookService:** Manages the core business logic for books, including searching, retrieving details, and updating the book inventory. It ensures that book data is consistent and valid.
- **BorrowingService:** Handles the logic for borrowing and returning books. It checks for book availability, creates borrow requests, updates the number of available copies, and records the transaction in the user's borrowing history.
- **SearchService:** Implements the search functionality, allowing for efficient querying of the book database based on different criteria.

