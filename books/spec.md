# Module Specification: `Books`

**Version:** 2.0

**Author:** Karan Singh

**Date:** 2025-08-12

**Version History:**
- **v1.0 (2025-08-01):** Initial specification with core book management and borrowing functionality.
- **v2.0 (2025-08-12):** Added ISBN, publication date, cover image to Book model. Added book reservation and fine management functionality.

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
    -   Book reservations for items that are currently out of stock.
    -   Fines or penalties for overdue books.
-   **OUT OF SCOPE:**
    -   Managing book categories or genres as separate entities.
    -   Online payment processing for fines.

---

## 2. Dependencies

-   **`users` module**: Depends on the `users` module to link borrow records to specific users and to check user roles for permissions.

---

## 3. Data Models / Schema

### 3.1. `Book`

**Description:** Represents a single book title in the library's collection.

| Field Name          | Data Type             | Description                                                  |
| ------------------- | --------------------- | ------------------------------------------------------------ |
| `id`                | `PK`                  | The primary key.                                             |
| `title`             | `CharField(255)`      | The title of the book.                                       |
| `author`            | `CharField(255)`      | The author of the book.                                      |
| `genre`             | `CharField(100)`      | The genre of the book.                                       |
| `isbn`              | `CharField(13)`       | International Standard Book Number (ISBN-13 format).         |
| `publication_date`  | `DateField`           | The date when the book was published.                        |
| `cover_image_url`   | `URLField`            | URL to the book's cover image.                               |
| `quantity`          | `PositiveIntegerField`| The total number of copies of the book available to be borrowed. |
| `created_at`        | `DateTimeField`       | Timestamp of when the record was created.                    |
| `updated_at`        | `DateTimeField`       | Timestamp of the last update.                                |

### 3.2. `BorrowRecord`

**Description:** Tracks the status and history of a single borrowing transaction.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `user`          | `ForeignKey` to `User`                  | The user who is borrowing the book.                          |
| `book`          | `ForeignKey` to `Book`                  | The book being borrowed.                                     |
| `borrow_date`   | `DateField`                             | The date the borrow request was approved. Null until approval. |
| `due_date`      | `DateField`                             | The date by which the book must be returned. Set when borrow is approved. |
| `return_date`   | `DateField`                             | The date the book was returned. Null until returned.         |
| `status`        | `CharField(20)`                         | The current status of the borrow request. Choices: `PENDING`, `APPROVED`, `REJECTED`, `RETURNED`. Default: `PENDING`. |
| `created_at`    | `DateTimeField`                         | Timestamp of when the borrow request was created.            |
| `updated_at`    | `DateTimeField`                         | Timestamp of the last status update.                         |

### 3.3. `Reservation`

**Description:** Represents a member's reservation for a book that is currently unavailable.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `user`          | `ForeignKey` to `User`                  | The user who is reserving the book.                          |
| `book`          | `ForeignKey` to `Book`                  | The book being reserved.                                     |
| `status`        | `CharField(20)`                         | The current status of the reservation. Choices: `PENDING`, `FULFILLED`, `CANCELLED`. Default: `PENDING`. |
| `reservation_date` | `DateTimeField`                      | Timestamp of when the reservation was created.               |
| `notification_sent` | `BooleanField`                      | Whether the user has been notified that the book is available. Default: `False`. |
| `created_at`    | `DateTimeField`                         | Timestamp of when the record was created.                    |
| `updated_at`    | `DateTimeField`                         | Timestamp of the last update.                                |

### 3.4. `Fine`

**Description:** Tracks fines imposed on members for overdue books.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `borrow_record` | `ForeignKey` to `BorrowRecord`          | The borrow record associated with this fine.                 |
| `user`          | `ForeignKey` to `User`                  | The user who is being fined.                                 |
| `amount`        | `DecimalField(6,2)`                     | The amount of the fine.                                      |
| `reason`        | `CharField(255)`                        | The reason for the fine (e.g., "Overdue return").            |
| `status`        | `CharField(20)`                         | The current status of the fine. Choices: `PENDING`, `PAID`, `WAIVED`. Default: `PENDING`. |
| `days_overdue`  | `PositiveIntegerField`                  | The number of days the book was overdue.                     |
| `created_at`    | `DateTimeField`                         | Timestamp of when the fine was created.                      |
| `updated_at`    | `DateTimeField`                         | Timestamp of the last update.                                |

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
    -   **Request Body:** `{ "title": "string", "author": "string", "genre": "string", "isbn": "string", "publication_date": "date", "cover_image_url": "string", "quantity": "int" }`
    -   **Success Response (201 Created):** `{ "id": "int", ... }`

-   **`GET /api/books/{id}/`**
    -   **Description:** Retrieves a single book by its ID.
    -   **Permissions:** Authenticated users
    -   **Success Response (200 OK):** `{ "id": "int", ... }`
    -   **Failure Response (404 Not Found):** If the book ID does not exist.

-   **`PUT /api/books/{id}/`**
    -   **Description:** Updates all fields of a specific book.
    -   **Permissions:** Admin only
    -   **Request Body:** `{ "title": "string", "author": "string", "genre": "string", "isbn": "string", "publication_date": "date", "cover_image_url": "string", "quantity": "int" }`
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
    -   **Description:** Allows a member to return a book they have borrowed. Automatically calculates and creates fines if the book is overdue.
    -   **Permissions:** Authenticated users (members)
    -   **Request Body:** `{ "borrow_record_id": "int" }`
    -   **Success Response (200 OK):** `{ "message": "Book returned successfully.", "fine": { "amount": "decimal", "days_overdue": "int" } }` or `{ "message": "Book returned successfully." }` if no fine.
    -   **Failure Response (400 Bad Request):** If the record ID is invalid or does not belong to the user.

### 4.3. `Reservation` Endpoints

-   **`POST /api/books/reserve/`**
    -   **Description:** Allows a member to reserve a book that is currently unavailable (quantity = 0).
    -   **Permissions:** Authenticated users (members)
    -   **Request Body:** `{ "book_id": "int" }`
    -   **Success Response (201 Created):** `{ "message": "Book reserved successfully. You will be notified when it becomes available." }`
    -   **Failure Response (400 Bad Request):** If the book is available (should borrow instead) or user already has a pending reservation for this book.

-   **`GET /api/books/reservations/`**
    -   **Description:** Allows a member to view their book reservations.
    -   **Permissions:** Authenticated users (members)
    -   **Success Response (200 OK):** `[ { "id": "int", "book": { ... }, "status": "string", "reservation_date": "datetime" }, ... ]`

-   **`DELETE /api/books/reservations/{id}/`**
    -   **Description:** Allows a member to cancel their reservation.
    -   **Permissions:** Authenticated users (members)
    -   **Success Response (204 No Content):**
    -   **Failure Response (404 Not Found):** If the reservation ID does not exist or does not belong to the user.

### 4.4. `Fine` Endpoints

-   **`GET /api/books/fines/`**
    -   **Description:** Allows a member to view their fines.
    -   **Permissions:** Authenticated users (members)
    -   **Success Response (200 OK):** `[ { "id": "int", "amount": "decimal", "reason": "string", "status": "string", "book": { "title": "string" } }, ... ]`

### 4.5. `Admin Borrowing` Endpoints

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

### 4.6. `Admin Reservation` Endpoints

-   **`GET /api/admin/reservations/`**
    -   **Description:** Retrieves a list of all book reservations. Can be filtered by status.
    -   **Permissions:** Admin only
    -   **Query Params:** `?status=[PENDING/FULFILLED/CANCELLED]`
    -   **Success Response (200 OK):** `[ { "id": "int", "user": { ... }, "book": { ... }, "status": "string" }, ... ]`

-   **`PATCH /api/admin/reservations/{id}/fulfill/`**
    -   **Description:** Marks a reservation as fulfilled when the book becomes available and is set aside for the member.
    -   **Permissions:** Admin only
    -   **Request Body:** (empty)
    -   **Success Response (200 OK):** `{ "message": "Reservation fulfilled. Member has been notified." }`

### 4.7. `Admin Fine` Endpoints

-   **`GET /api/admin/fines/`**
    -   **Description:** Retrieves a list of all fines. Can be filtered by status.
    -   **Permissions:** Admin only
    -   **Query Params:** `?status=[PENDING/PAID/WAIVED]&user_id=[int]`
    -   **Success Response (200 OK):** `[ { "id": "int", "user": { ... }, "borrow_record": { ... }, "amount": "decimal", "status": "string" }, ... ]`

-   **`PATCH /api/admin/fines/{id}/mark-as-paid/`**
    -   **Description:** Marks a fine as paid.
    -   **Permissions:** Admin only
    -   **Request Body:** (empty)
    -   **Success Response (200 OK):** `{ "message": "Fine marked as paid." }`

-   **`PATCH /api/admin/fines/{id}/waive/`**
    -   **Description:** Waives a fine.
    -   **Permissions:** Admin only
    -   **Request Body:** (empty)
    -   **Success Response (200 OK):** `{ "message": "Fine waived." }`

---

## 5. Services and Business Logic

### 5.1. `BorrowingService`

-   **Purpose:** To manage the state transitions of a `BorrowRecord` and its side effects.
-   **Methods:**
    -   `request_borrow(user, book)`: Checks if the book is available. Creates a new `BorrowRecord` with `PENDING` status.
    -   `approve_request(borrow_record)`: Sets the record's status to `APPROVED`, sets the `borrow_date` and `due_date` (typically 14 days from approval), and decrements the associated book's `quantity`.
    -   `reject_request(borrow_record)`: Sets the record's status to `REJECTED`.
    -   `return_book(borrow_record)`: Sets the record's status to `RETURNED`, sets the `return_date`, increments the associated book's `quantity`, and calculates any applicable fines for overdue returns.

### 5.2. `ReservationService`

-   **Purpose:** To manage book reservations and their fulfillment.
-   **Methods:**
    -   `reserve_book(user, book)`: Checks if the book is unavailable and creates a new `Reservation` with `PENDING` status.
    -   `fulfill_reservation(reservation)`: Marks the reservation as `FULFILLED` and notifies the user that the book is available for them.
    -   `cancel_reservation(reservation)`: Marks the reservation as `CANCELLED`.
    -   `check_for_available_reservations(book)`: When a book is returned, checks if there are any pending reservations for it and fulfills the oldest one.

### 5.3. `FineService`

-   **Purpose:** To manage fines for overdue books.
-   **Methods:**
    -   `calculate_fine(borrow_record)`: Calculates the fine amount based on the number of days overdue (typically $0.50 per day).
    -   `create_fine(borrow_record, amount, reason)`: Creates a new `Fine` record associated with the borrow record.
    -   `mark_as_paid(fine)`: Sets the fine's status to `PAID`.
    -   `waive_fine(fine)`: Sets the fine's status to `WAIVED`.

---

## 6. Events (Optional)

-   **Publishes:**
    -   `borrow.request.created`: When a member requests a book. Carries `record_id`, `user_id`, `book_id`.
    -   `borrow.request.approved`: When an admin approves a request. Carries `record_id`.
    -   `borrow.request.rejected`: When an admin rejects a request. Carries `record_id`.
    -   `book.returned`: When a member returns a book. Carries `record_id`.
    -   `book.reservation.created`: When a member reserves a book. Carries `reservation_id`, `user_id`, `book_id`.
    -   `book.reservation.fulfilled`: When a reservation is fulfilled. Carries `reservation_id`.
    -   `book.reservation.cancelled`: When a reservation is cancelled. Carries `reservation_id`.
    -   `fine.created`: When a fine is created for an overdue book. Carries `fine_id`, `user_id`, `amount`.
    -   `fine.paid`: When a fine is marked as paid. Carries `fine_id`.
    -   `fine.waived`: When a fine is waived. Carries `fine_id`.