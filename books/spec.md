# Module Specification: `Books`

**Version:** 1.0

**Author:** Gemini

**Date:** 2025-08-01

---

## 1. Purpose and Responsibility

**Description:** This module is responsible for managing the library's book catalog and handling the entire book borrowing lifecycle, from request to return.

**Scope:**
-   **IN SCOPE:**
    -   Managing the book inventory (CRUD operations on books).
    -   Allowing members to search for books.
    -   Handling member requests to borrow books.
    -   Admin approval or rejection of borrow requests.
    -   Tracking the history of borrowed books.
-   **OUT OF SCOPE:**
    -   Managing book categories or genres as separate entities.
    -   Handling book reservations for items that are currently out of stock.
    -   Fines or penalties for overdue books.

---

## 2. Dependencies

-   **`users` module**: Depends on the `users` module to link borrow records to specific users and to check user roles for permissions.

---

## 3. Data Models / Schema

### 3.1. `Book`

**Description:** Represents a single book title in the library's collection.

| Field Name      | Data Type             | Description                                                  |
| --------------- | --------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                  | The primary key.                                             |
| `title`         | `CharField(255)`      | The title of the book.                                       |
| `author`        | `CharField(255)`      | The author of the book.                                      |
| `genre`         | `CharField(100)`      | The genre of the book.                                       |
| `quantity`      | `PositiveIntegerField`| The number of available copies to borrow. |
| `created_at`    | `DateTimeField`       | Timestamp of when the record was created.                    |
| `updated_at`    | `DateTimeField`       | Timestamp of the last update.                                |

### 3.2. `BorrowRecord`

**Description:** Tracks the status and history of a single borrowing transaction.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `user`          | `ForeignKey` to `User`                  | The user who is borrowing the book.                          |
| `book`          | `ForeignKey` to `Book`                  | The book being borrowed.                                     |
| `request_date`  | `DateTimeField`                         | The timestamp when the borrow request was created.           |
| `borrow_date`   | `DateTimeField`                         | The timestamp when the request was approved. Null until approval. |
| `return_date`   | `DateTimeField`                         | The timestamp when the book was returned. Null until returned. |
| `status`        | `CharField(20)`                         | The current status of the borrow request. Choices: `PENDING`, `APPROVED`, `REJECTED`, `RETURNED`. Default: `PENDING`. |
| `created_at`    | `DateTimeField`                         | Timestamp of when the borrow request was created.            |
| `updated_at`    | `DateTimeField`                         | Timestamp of the last status update.                         |

---

## 4. API Endpoints

**Base URL:** `/api/books/`

### 4.1. `Book` Endpoints

-   **`GET /api/books/`**
    -   **Description:** Retrieves a list of all books in the catalog. Supports searching.
    -   **Permissions:** Authenticated users
    -   **Query Params:** `?search=[query]` to search by title, author, or genre.
    -   **Success Response (200 OK):** `[ { "id": "int", "title": "string", "author": "string", "genre": "string", "quantity": "int" }, ... ]`

-   **`POST /api/books/`**
    -   **Description:** Creates a new book entry in the catalog.
    -   **Permissions:** Admin only
    -   **Request Body:** `{ "title": "string", "author": "string", "genre": "string", "quantity": "int" }`
    -   **Success Response (201 Created):** `{ "id": "int", ... }`

-   **`GET /api/books/{id}/`**
    -   **Description:** Retrieves a single book by its ID.
    -   **Permissions:** Authenticated users
    -   **Success Response (200 OK):** `{ "id": "int", ... }`
    -   **Failure Response (404 Not Found):** If the book ID does not exist.

-   **`PUT /api/books/{id}/`**
    -   **Description:** Updates all fields of a specific book.
    -   **Permissions:** Admin only
    -   **Request Body:** `{ "title": "string", "author": "string", "genre": "string", "quantity": "int" }`
    -   **Success Response (200 OK):** `{ "id": "int", ... }`

-   **`DELETE /api/books/{id}/`**
    -   **Description:** Deletes a book from the catalog.
    -   **Permissions:** Admin only
    -   **Success Response (204 No Content):**

### 4.2. `Borrowing` Endpoints

-   **`POST /api/books/borrow/`**
    -   **Description:** Allows a member to submit a request to borrow a book.
    -   **Permissions:** Authenticated users (members)
    -   **Request Body:** `{ "book_id": "int" }`
    -   **Success Response (201 Created):** `{ "message": "Borrow request submitted successfully. Waiting for admin approval." }`
    -   **Failure Response (400 Bad Request):** If book quantity is 0 or the user has an outstanding request for the same book.

-   **`POST /api/books/return/`**
    -   **Description:** Allows a member to return a book they have borrowed.
    -   **Permissions:** Authenticated users (members)
    -   **Request Body:** `{ "borrow_record_id": "int" }`
    -   **Success Response (200 OK):** `{ "message": "Book returned successfully." }`
    -   **Failure Response (400 Bad Request):** If the record ID is invalid or does not belong to the user.

### 4.3. `Admin Borrowing` Endpoints

-   **`GET /api/admin/borrow/`**
    -   **Description:** Retrieves a list of all borrow records. Can be filtered by status.
    -   **Permissions:** Admin only
    -   **Query Params:** `?status=[PENDING/APPROVED/REJECTED/RETURNED]`
    -   **Success Response (200 OK):** `[ { "id": "int", "user": { ... }, "book": { ... }, "status": "string" }, ... ]`

-   **`PATCH /api/admin/borrow/{id}/approve/`**
    -   **Description:** Approves a pending borrow request.
    -   **Permissions:** Admin only
    -   **Request Body:** (empty)
    -   **Success Response (200 OK):** `{ "message": "Borrow request approved." }`
    -   **Failure Response (400 Bad Request):** If the request is not in `PENDING` state or book quantity is 0.

-   **`PATCH /api/admin/borrow/{id}/reject/`**
    -   **Description:** Rejects a pending borrow request.
    -   **Permissions:** Admin only
    -   **Request Body:** (empty)
    -   **Success Response (200 OK):** `{ "message": "Borrow request rejected." }`

---

## 5. Services and Business Logic

### 5.1. `BorrowingService`

-   **Purpose:** To manage the state transitions of a `BorrowRecord` and its side effects.
-   **Methods:**
    -   `request_borrow(user, book)`: Checks if the book is available. Creates a new `BorrowRecord` with `PENDING` status.
    -   `approve_request(borrow_record)`: Sets the record's status to `APPROVED`, sets the `borrow_date`, and decrements the associated book's `quantity`.
    -   `reject_request(borrow_record)`: Sets the record's status to `REJECTED`.
    -   `return_book(borrow_record)`: Sets the record's status to `RETURNED`, sets the `return_date`, and increments the associated book's `quantity`.

---

## 6. Events (Optional)

-   **Publishes:**
    -   `borrow.request.created`: When a member requests a book. Carries `record_id`, `user_id`, `book_id`.
    -   `borrow.request.approved`: When an admin approves a request. Carries `record_id`.
    -   `borrow.request.rejected`: When an admin rejects a request. Carries `record_id`.
    -   `book.returned`: When a member returns a book. Carries `record_id`.