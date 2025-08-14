# Module Specification: `Books` v2.0

**Version:** 2.0

**Author:** Library Management System Team

**Date:** 2025-08-08

**Previous Version:** v1.0 (Basic book management and borrowing workflow)

---

## 1. Purpose and Responsibility

**Description:** This module is responsible for managing the library's book catalog, handling the entire book borrowing lifecycle, fine management for overdue books, and providing data for automated reporting. It encompasses book inventory management, borrowing workflows, reservation systems, and integration with reporting systems.

**Scope:**
-   **IN SCOPE:**
    -   Enhanced book model with ISBN, publication date, and cover images (NEW)
    -   Fine management for overdue books (NEW)
    -   Book reservation system for out-of-stock items (NEW)
    -   Integration with reporting system for activity statistics (NEW)
    -   Automatic fine calculation and notification (NEW)
    -   Advanced search and filtering capabilities (NEW)
    -   Book category management (NEW)
    -   Cover image processing and storage (NEW)
-   **OUT OF SCOPE:**
    -   E-book management or digital content delivery
    -   Inter-library loan systems
    -   Book recommendations engine

---

## 2. Dependencies

-   **`users` module**: For fine calculations based on borrowing activities and user validation.
-   **`reports` module**: For providing borrowing statistics and activity data for automated reports.
-   **`celery`**: For background tasks like fine calculations and overdue notifications.
-   **`Pillow`**: For image processing of book cover images.
-   **`django-storages`**: For cloud storage of book cover images.
-   **`django-filter`**: For advanced filtering capabilities.

---

## 3. Data Models / Schema

### 3.1. `Book` - ENHANCED

**Description:** Represents a single book title in the library's collection. Enhanced with additional fields for v2.0.

| Field Name      | Data Type             | Description                                                  |
| --------------- | --------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                  | The primary key.                                             |
| `title`         | `CharField(255)`      | The title of the book.                                       |
| `author`        | `CharField(255)`      | The author of the book.                                      |
| `genre`         | `CharField(100)`      | The genre of the book.                                       |
| `quantity`      | `PositiveIntegerField`| The total number of copies of the book available to be borrowed. |
| `created_at`    | `DateTimeField`       | Timestamp of when the record was created.                    |
| `updated_at`    | `DateTimeField`       | Timestamp of the last update.                                |
| `isbn`          | `CharField(13)`       | International Standard Book Number (NEW).                    |
| `publication_date` | `DateField`        | Date when the book was published (NEW).                      |
| `cover_image_url` | `URLField`         | URL to the book's cover image (NEW).                         |
| `cover_image`   | `ImageField`          | Local storage of book cover image (NEW).                     |
| `summary`       | `TextField`           | Brief description of the book (NEW).                         |
| `pages`         | `PositiveIntegerField`| Number of pages in the book (NEW).                           |
| `language`      | `CharField(10)`       | Language of the book (e.g., 'en', 'es', 'fr') (NEW).        |
| `publisher`     | `CharField(255)`      | Publisher of the book (NEW).                                 |
| `is_active`     | `BooleanField`        | Whether the book is available in the catalog (NEW).          |
| `edition`       | `CharField(50)`       | Edition of the book (NEW).                                   |
| `format`        | `CharField(20)`       | Book format (Hardcover, Paperback, etc.) (NEW).              |
| `price`         | `DecimalField(10,2)`  | Book price for fine calculations (NEW).                      |
| `condition`     | `CharField(20)`       | Book condition (NEW, EXCELLENT, GOOD, FAIR) (NEW).           |
| `location`      | `CharField(100)`      | Physical location in library (NEW).                          |
| `tags`          | `JSONField`           | Searchable tags for the book (NEW).                          |
| `rating`        | `DecimalField(3,2)`   | Average user rating (NEW).                                   |
| `rating_count`  | `PositiveIntegerField`| Number of ratings (NEW).                                     |

### 3.2. `BorrowRecord` - ENHANCED

**Description:** Tracks the status and history of a single borrowing transaction. Enhanced with additional fields for v2.0.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `user`          | `ForeignKey` to `User`                  | The user who is borrowing the book.                          |
| `book`          | `ForeignKey` to `Book`                  | The book being borrowed.                                     |
| `borrow_date`   | `DateField`                             | The date the borrow request was approved. Null until approval. |
| `return_date`   | `DateField`                             | The date the book was returned. Null until returned.         |
| `status`        | `CharField(20)`                         | The current status of the borrow request. Choices: `PENDING`, `APPROVED`, `REJECTED`, `RETURNED`. Default: `PENDING`. |
| `created_at`    | `DateTimeField`                         | Timestamp of when the borrow request was created.            |
| `updated_at`    | `DateTimeField`                         | Timestamp of the last status update.                         |
| `due_date`      | `DateField`                             | Date when the book should be returned (NEW).                 |
| `fine_amount`   | `DecimalField(10,2)`                    | Fine amount if book is overdue (NEW).                        |
| `fine_paid`     | `BooleanField`                          | Whether the fine has been paid (NEW).                        |
| `notes`         | `TextField`                             | Admin notes about the borrowing (NEW).                       |
| `return_condition` | `CharField(50)`                     | Condition of book when returned (NEW).                       |
| `extended_count` | `PositiveIntegerField`               | Number of times the due date was extended (NEW).             |
| `last_extension_date` | `DateField`                        | Date of last extension (NEW).                                |
| `fine_calculated_at` | `DateTimeField`                     | When fine was last calculated (NEW).                         |
| `overdue_notifications_sent` | `PositiveIntegerField`           | Number of overdue notifications sent (NEW).                  |

### 3.3. `BookReservation` - NEW MODEL

**Description:** Tracks reservations for books that are currently out of stock.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `user`          | `ForeignKey` to `User`                  | The user who made the reservation.                           |
| `book`          | `ForeignKey` to `Book`                  | The book being reserved.                                     |
| `status`        | `CharField(20)`                         | Reservation status. Choices: `PENDING`, `FULFILLED`, `CANCELLED`, `EXPIRED`. Default: `PENDING`. |
| `reserved_at`   | `DateTimeField`                         | When the reservation was made.                               |
| `expires_at`    | `DateTimeField`                         | When the reservation expires.                                |
| `fulfilled_at`  | `DateTimeField`                         | When the reservation was fulfilled.                          |
| `priority`      | `PositiveIntegerField`                  | Priority order of the reservation.                           |
| `notified`      | `BooleanField`                          | Whether user has been notified of availability.              |
| `notification_sent_at` | `DateTimeField`                     | When notification was sent (NEW).                            |
| `notes`         | `TextField`                             | Admin notes about the reservation (NEW).                     |
| `auto_fulfill`  | `BooleanField`                          | Whether to auto-fulfill when book becomes available (NEW).   |

### 3.4. `BookCategory` - NEW MODEL

**Description:** Categories for organizing books hierarchically.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `name`          | `CharField(100)`                        | Name of the category.                                        |
| `description`   | `TextField`                             | Description of the category.                                 |
| `parent`        | `ForeignKey` to `BookCategory`          | Parent category for hierarchical organization.               |
| `created_at`    | `DateTimeField`                         | When the category was created.                               |
| `is_active`     | `BooleanField`                          | Whether the category is active.                              |
| `sort_order`    | `PositiveIntegerField`                  | Order for display purposes.                                  |
| `icon`          | `CharField(50)`                         | Icon class for UI display.                                   |
| `color`         | `CharField(7)`                          | Color code for UI display.                                   |

### 3.5. `BookRating` - NEW MODEL

**Description:** User ratings and reviews for books.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `user`          | `ForeignKey` to `User`                  | The user who rated the book.                                 |
| `book`          | `ForeignKey` to `Book`                  | The book being rated.                                        |
| `rating`        | `PositiveIntegerField`                  | Rating (1-5 stars).                                          |
| `review`        | `TextField`                             | Optional review text.                                        |
| `created_at`    | `DateTimeField`                         | When the rating was created.                                 |
| `updated_at`    | `DateTimeField`                         | When the rating was last updated.                            |
| `is_public`     | `BooleanField`                          | Whether the review is public.                                |
| `helpful_votes` | `PositiveIntegerField`                  | Number of helpful votes.                                     |

### 3.6. `BookAuditLog` - NEW MODEL

**Description:** Audit trail for book-related operations.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `book`          | `ForeignKey` to `Book`                  | The book being audited.                                      |
| `action`        | `CharField(50)`                         | Action performed (CREATE, UPDATE, DELETE, BORROW, RETURN).   |
| `performed_by`  | `ForeignKey` to `User`                  | User who performed the action.                               |
| `old_values`    | `JSONField`                             | Previous values before change.                               |
| `new_values`    | `JSONField`                             | New values after change.                                     |
| `created_at`    | `DateTimeField`                         | When the action was performed.                               |
| `ip_address`    | `GenericIPAddressField`                 | IP address of the user.                                      |
| `user_agent`    | `TextField`                             | User agent string.                                           |

---

## 4. API Endpoints

**Base URL:** `/api/books/`

### 4.1. `Enhanced Book Management` Endpoints (NEW)

-   **`POST /api/books/{id}/upload-cover/`**
    -   **Description:** Uploads a cover image for a book with processing and optimization.
    -   **Permissions:** Admin only
    -   **Request Body:** Form data with image file (JPEG, PNG, WebP)
    -   **Success Response (200 OK):** `{ "message": "Cover image uploaded successfully.", "image_url": "string", "thumbnail_url": "string", "file_size": "int" }`
    -   **Error Response (400 Bad Request):** `{ "error": "Invalid image format. Supported formats: JPEG, PNG, WebP." }`
    -   **Error Response (413 Payload Too Large):** `{ "error": "Image file too large. Maximum size: 5MB." }`

-   **`GET /api/books/search/`**
    -   **Description:** Advanced book search with multiple filters and sorting options.
    -   **Permissions:** Authenticated users
    -   **Query Params:** `?q=string&author=string&genre=string&isbn=string&publisher=string&language=string&format=string&min_pages=int&max_pages=int&available=true/false&rating_min=decimal&publication_year=int&sort_by=title/author/rating/publication_date&order=asc/desc&page=int&page_size=int`
    -   **Success Response (200 OK):** `{ "count": "int", "next": "string", "previous": "string", "results": [ { "id": "int", "title": "string", "author": "string", "genre": "string", "quantity": "int", "isbn": "string", "publication_date": "date", "cover_image_url": "string", "summary": "string", "pages": "int", "language": "string", "publisher": "string", "rating": "decimal", "rating_count": "int", "available": "boolean" }, ... ] }`

-   **`GET /api/books/{id}/details/`**
    -   **Description:** Retrieves comprehensive book details including ratings and availability.
    -   **Permissions:** Authenticated users
    -   **Success Response (200 OK):** `{ "id": "int", "title": "string", "author": "string", "genre": "string", "quantity": "int", "isbn": "string", "publication_date": "date", "cover_image_url": "string", "summary": "string", "pages": "int", "language": "string", "publisher": "string", "edition": "string", "format": "string", "price": "decimal", "condition": "string", "location": "string", "tags": "array", "rating": "decimal", "rating_count": "int", "available": "boolean", "reservations_count": "int", "borrow_history": [ ... ] }`

-   **`POST /api/books/{id}/rate/`**
    -   **Description:** Allows users to rate and review a book.
    -   **Permissions:** Authenticated users
    -   **Request Body:** `{ "rating": "int", "review": "string", "is_public": "boolean" }`
    -   **Success Response (201 Created):** `{ "message": "Rating submitted successfully.", "average_rating": "decimal", "total_ratings": "int" }`
    -   **Error Response (400 Bad Request):** `{ "error": "Rating must be between 1 and 5." }`

### 4.2. `Enhanced Borrowing` Endpoints (NEW)

-   **`GET /api/books/my-borrows/`**
    -   **Description:** Retrieves the current user's borrowing history with detailed information.
    -   **Permissions:** Authenticated users
    -   **Query Params:** `?status=PENDING/APPROVED/RETURNED&overdue=true/false&sort_by=borrow_date/due_date&order=asc/desc&page=int&page_size=int`
    -   **Success Response (200 OK):** `{ "count": "int", "next": "string", "previous": "string", "results": [ { "id": "int", "book": { ... }, "borrow_date": "date", "due_date": "date", "status": "string", "fine_amount": "decimal", "days_overdue": "int", "can_extend": "boolean", "extended_count": "int" }, ... ] }`

-   **`POST /api/books/borrow/{id}/extend/`**
    -   **Description:** Extends the due date for a borrowed book.
    -   **Permissions:** Authenticated users
    -   **Request Body:** `{ "extension_days": "int" }`
    -   **Success Response (200 OK):** `{ "message": "Due date extended successfully.", "new_due_date": "date", "extension_count": "int" }`
    -   **Error Response (400 Bad Request):** `{ "error": "Maximum extensions reached for this book." }`

-   **`POST /api/books/return/`** (ENHANCED)
    -   **Description:** Returns a borrowed book with condition assessment and fine calculation.
    -   **Permissions:** Authenticated users
    -   **Request Body:** `{ "borrow_record_id": "int", "return_condition": "string", "damage_notes": "string" }`
    -   **Success Response (200 OK):** `{ "message": "Book returned successfully.", "fine_amount": "decimal", "damage_fine": "decimal", "total_fine": "decimal", "condition_assessed": "string" }`

### 4.3. `Reservation System` Endpoints (NEW)

-   **`POST /api/books/reserve/`**
    -   **Description:** Allows a member to reserve a book that is out of stock.
    -   **Permissions:** Authenticated users
    -   **Request Body:** `{ "book_id": "int", "auto_fulfill": "boolean" }`
    -   **Success Response (201 Created):** `{ "message": "Book reserved successfully.", "reservation_id": "int", "position_in_queue": "int", "estimated_wait_time": "string" }`
    -   **Error Response (400 Bad Request):** `{ "error": "You already have a reservation for this book." }`

-   **`GET /api/books/my-reservations/`**
    -   **Description:** Retrieves the current user's book reservations with status updates.
    -   **Permissions:** Authenticated users
    -   **Query Params:** `?status=PENDING/FULFILLED/CANCELLED&sort_by=reserved_at/priority&order=asc/desc`
    -   **Success Response (200 OK):** `[ { "id": "int", "book": { ... }, "status": "string", "reserved_at": "datetime", "expires_at": "datetime", "position_in_queue": "int", "estimated_wait_time": "string", "notified": "boolean" }, ... ]`

-   **`DELETE /api/books/reserve/{id}/cancel/`**
    -   **Description:** Cancels a book reservation.
    -   **Permissions:** Authenticated users
    -   **Success Response (200 OK):** `{ "message": "Reservation cancelled successfully." }`

-   **`GET /api/books/admin/reservations/`**
    -   **Description:** Retrieves all book reservations with management options.
    -   **Permissions:** Admin only
    -   **Query Params:** `?status=PENDING/FULFILLED/CANCELLED&book_id=int&user_id=int&overdue=true/false&sort_by=reserved_at/priority&order=asc/desc&page=int&page_size=int`
    -   **Success Response (200 OK):** `{ "count": "int", "next": "string", "previous": "string", "results": [ { "id": "int", "user": { ... }, "book": { ... }, "status": "string", "priority": "int", "reserved_at": "datetime", "expires_at": "datetime", "position_in_queue": "int" }, ... ] }`

-   **`POST /api/books/admin/reservations/{id}/fulfill/`**
    -   **Description:** Manually fulfills a reservation when book becomes available.
    -   **Permissions:** Admin only
    -   **Success Response (200 OK):** `{ "message": "Reservation fulfilled successfully.", "notification_sent": "boolean" }`

### 4.4. `Overdue Management` Endpoints (NEW)

-   **`GET /api/books/admin/overdue/`**
    -   **Description:** Retrieves all overdue books with fine calculations and user information.
    -   **Permissions:** Admin only
    -   **Query Params:** `?days_overdue_min=int&days_overdue_max=int&fine_amount_min=decimal&fine_amount_max=decimal&user_id=int&sort_by=days_overdue/fine_amount/due_date&order=asc/desc&page=int&page_size=int`
    -   **Success Response (200 OK):** `{ "count": "int", "next": "string", "previous": "string", "results": [ { "id": "int", "user": { ... }, "book": { ... }, "days_overdue": "int", "fine_amount": "decimal", "due_date": "date", "last_notification_sent": "datetime", "notifications_sent": "int" }, ... ] }`

-   **`POST /api/books/admin/overdue/send-notifications/`**
    -   **Description:** Sends overdue notifications to users with overdue books.
    -   **Permissions:** Admin only
    -   **Request Body:** `{ "user_ids": [int], "notification_type": "email/sms/both", "custom_message": "string" }`
    -   **Success Response (200 OK):** `{ "message": "Notifications sent successfully.", "sent_count": "int", "failed_count": "int", "failed_users": [ ... ] }`

-   **`POST /api/books/admin/overdue/calculate-fines/`**
    -   **Description:** Recalculates fines for all overdue books.
    -   **Permissions:** Admin only
    -   **Success Response (200 OK):** `{ "message": "Fines calculated successfully.", "books_processed": "int", "fines_created": "int", "total_fine_amount": "decimal" }`

### 4.5. `Statistics and Reporting` Endpoints (NEW)

-   **`GET /api/books/admin/statistics/`**
    -   **Description:** Retrieves comprehensive book borrowing statistics for reports.
    -   **Permissions:** Admin only
    -   **Query Params:** `?start_date=date&end_date=date&group_by=day/week/month&include_details=true/false`
    -   **Success Response (200 OK):** `{ "total_borrows": "int", "overdue_books": "int", "total_fines": "decimal", "fines_collected": "decimal", "most_borrowed_books": [ { "book": { ... }, "borrow_count": "int", "total_fines": "decimal" }, ... ], "popular_genres": [ { "genre": "string", "borrow_count": "int", "percentage": "decimal" }, ... ], "daily_stats": [ { "date": "date", "borrows": "int", "returns": "int", "fines": "decimal" }, ... ], "user_activity": [ { "user": { ... }, "borrow_count": "int", "overdue_count": "int", "total_fines": "decimal" }, ... ] }`

-   **`GET /api/books/admin/statistics/export/`**
    -   **Description:** Exports book statistics in various formats for reporting.
    -   **Permissions:** Admin only
    -   **Query Params:** `?start_date=date&end_date=date&format=csv/excel/pdf&report_type=borrowing/overdue/fines`
    -   **Success Response (200 OK):** File download with appropriate content type

-   **`GET /api/books/admin/statistics/dashboard/`**
    -   **Description:** Retrieves real-time dashboard statistics.
    -   **Permissions:** Admin only
    -   **Success Response (200 OK):** `{ "total_books": "int", "available_books": "int", "borrowed_books": "int", "overdue_books": "int", "pending_requests": "int", "active_reservations": "int", "today_borrows": "int", "today_returns": "int", "today_fines": "decimal", "weekly_trend": [ ... ], "top_books": [ ... ], "recent_activities": [ ... ] }`

### 4.6. `Category Management` Endpoints (NEW)

-   **`GET /api/books/categories/`**
    -   **Description:** Retrieves all book categories with hierarchical structure.
    -   **Permissions:** Authenticated users
    -   **Success Response (200 OK):** `[ { "id": "int", "name": "string", "description": "string", "parent": "int", "is_active": "boolean", "sort_order": "int", "icon": "string", "color": "string", "book_count": "int", "children": [ ... ] }, ... ]`

-   **`POST /api/books/admin/categories/`**
    -   **Description:** Creates a new book category.
    -   **Permissions:** Admin only
    -   **Request Body:** `{ "name": "string", "description": "string", "parent": "int", "sort_order": "int", "icon": "string", "color": "string" }`
    -   **Success Response (201 Created):** `{ "id": "int", "name": "string", ... }`

-   **`PUT /api/books/admin/categories/{id}/`**
    -   **Description:** Updates a book category.
    -   **Permissions:** Admin only
    -   **Request Body:** `{ "name": "string", "description": "string", "parent": "int", "sort_order": "int", "icon": "string", "color": "string", "is_active": "boolean" }`
    -   **Success Response (200 OK):** `{ "id": "int", "name": "string", ... }`

-   **`DELETE /api/books/admin/categories/{id}/`**
    -   **Description:** Deletes a book category (only if no books are assigned).
    -   **Permissions:** Admin only
    -   **Success Response (204 No Content):**

---

## 5. Services and Business Logic

### 5.1. `Enhanced BorrowingService` (NEW)

-   **Purpose:** To manage the state transitions of a `BorrowRecord` with enhanced functionality.
-   **Methods:**
    -   `request_borrow(user, book)`: Enhanced to check user fines, membership status, and reservation priority.
    -   `approve_request(borrow_record, due_date=None, notes=None)`: Enhanced with due date calculation, notes, and reservation fulfillment.
    -   `reject_request(borrow_record, reason)`: Sets the record's status to `REJECTED` with reason.
    -   `return_book(borrow_record, return_condition, damage_notes)`: Enhanced with fine calculation, condition assessment, and damage fines.
    -   `extend_due_date(borrow_record, extension_days)`: Extends due date with validation and limits.
    -   `calculate_due_date(borrow_date, user_role, book_type)`: Calculates due date based on user role and book type.
    -   `check_overdue_books()`: Finds all overdue books and calculates fines.
    -   `process_overdue_fines()`: Processes fines for overdue books with notifications.
    -   `calculate_damage_fine(book, damage_level, damage_notes)`: Calculates fine for damaged books.
    -   `send_overdue_notifications()`: Sends overdue notifications to users.

### 5.2. `BookManagementService` (NEW)

-   **Purpose:** To handle enhanced book management operations.
-   **Methods:**
    -   `create_book(book_data, cover_image=None)`: Creates book with cover image processing and validation.
    -   `update_book(book, book_data, cover_image=None)`: Updates book with image handling and audit logging.
    -   `delete_book(book)`: Soft deletes book with dependency checks.
    -   `search_books(filters, user)`: Advanced book search with multiple filters and relevance scoring.
    -   `get_book_statistics(start_date, end_date)`: Gets comprehensive book borrowing statistics.
    -   `process_cover_image(image_file)`: Processes and stores book cover images with optimization.
    -   `validate_isbn(isbn)`: Validates ISBN format and checksum.
    -   `import_books_from_csv(csv_file)`: Bulk import books from CSV file.
    -   `export_books_to_csv(filters)`: Exports books to CSV format.
    -   `update_book_ratings(book)`: Updates book rating statistics.

### 5.3. `ReservationService` (NEW)

-   **Purpose:** To handle book reservation operations.
-   **Methods:**
    -   `create_reservation(user, book, auto_fulfill=True)`: Creates a new book reservation with priority calculation.
    -   `fulfill_reservation(reservation)`: Fulfills a reservation when book becomes available.
    -   `cancel_reservation(reservation)`: Cancels a book reservation and updates queue.
    -   `notify_available_reservations(book)`: Notifies users when reserved books become available.
    -   `cleanup_expired_reservations()`: Removes expired reservations.
    -   `calculate_wait_time(reservation)`: Calculates estimated wait time for reservation.
    -   `get_reservation_queue(book)`: Gets current reservation queue for a book.
    -   `process_reservation_queue(book)`: Processes reservation queue when book becomes available.

### 5.4. `FineCalculationService` (NEW)

-   **Purpose:** To handle fine calculations and management.
-   **Methods:**
    -   `calculate_overdue_fine(borrow_record)`: Calculates fine for overdue book based on library policy.
    -   `calculate_damage_fine(book_value, damage_level, damage_notes)`: Calculates fine for damaged books.
    -   `apply_fine_policy(user_role, days_overdue, book_value)`: Applies fine policy based on user role and book value.
    -   `generate_fine_notification(user, fine)`: Generates fine notification for user.
    -   `process_fine_payment(fine, payment_method, reference)`: Processes fine payment with receipt.
    -   `waive_fine(fine, reason, waived_by)`: Waives a fine with audit trail.
    -   `calculate_fine_statistics(start_date, end_date)`: Calculates fine statistics for reporting.
    -   `send_fine_reminders()`: Sends reminder notifications for unpaid fines.

### 5.5. `ReportingService` (NEW)

-   **Purpose:** To provide data for automated reports and analytics.
-   **Methods:**
    -   `get_weekly_borrowing_stats(start_date, end_date)`: Gets weekly borrowing statistics.
    -   `get_most_borrowed_books(limit=10, start_date=None, end_date=None)`: Gets most borrowed books.
    -   `get_popular_genres(start_date=None, end_date=None)`: Gets popular book genres.
    -   `get_overdue_statistics(start_date=None, end_date=None)`: Gets overdue book statistics.
    -   `get_fine_statistics(start_date=None, end_date=None)`: Gets fine-related statistics.
    -   `get_user_activity_stats(start_date=None, end_date=None)`: Gets user activity statistics.
    -   `generate_weekly_report(start_date, end_date)`: Generates comprehensive weekly report.
    -   `export_report_data(report_type, start_date, end_date, format)`: Exports report data in various formats.
    -   `get_dashboard_statistics()`: Gets real-time dashboard statistics.

### 5.6. `ImageProcessingService` (NEW)

-   **Purpose:** To handle book cover image processing and storage.
-   **Methods:**
    -   `process_cover_image(image_file, book_id)`: Processes and optimizes cover images.
    -   `generate_thumbnail(image_file, size)`: Generates thumbnail images.
    -   `validate_image_format(image_file)`: Validates image format and size.
    -   `store_image(image_file, path)`: Stores image in cloud storage.
    -   `delete_image(image_path)`: Deletes image from storage.
    -   `get_image_url(image_path)`: Gets public URL for image.
    -   `optimize_image_quality(image_file)`: Optimizes image quality and size.

---

## 6. Code Changes Required

### 6.1. Model Changes

**File: `books/models.py`**
- Add new fields to Book model: `isbn`, `publication_date`, `cover_image_url`, `cover_image`, `summary`, `pages`, `language`, `publisher`, `is_active`, `edition`, `format`, `price`, `condition`, `location`, `tags`, `rating`, `rating_count`
- Add new fields to BorrowRecord model: `due_date`, `fine_amount`, `fine_paid`, `notes`, `return_condition`, `extended_count`, `last_extension_date`, `fine_calculated_at`, `overdue_notifications_sent`
- Create new models: `BookReservation`, `BookCategory`, `BookRating`, `BookAuditLog`
- Add model methods for fine calculations, due date management, and rating updates
- Add custom managers for book search and statistics
- Add model validation methods for ISBN, publication dates, and fine calculations

### 6.2. Serializer Changes

**File: `books/serializers.py`**
- Create `EnhancedBookSerializer` with all new fields and nested serialization
- Create `BookReservationSerializer` for reservations with queue position
- Create `BorrowRecordDetailSerializer` with fine information and extension details
- Create `BookStatisticsSerializer` for reporting with aggregated data
- Create `BookCategorySerializer` for hierarchical category management
- Create `BookRatingSerializer` for user ratings and reviews
- Create `BookSearchSerializer` for advanced search functionality
- Update existing serializers to include new fields and validation
- Add custom validation methods for ISBN, publication dates, and fine amounts

### 6.3. View Changes

**File: `books/views.py`**
- Add reservation management views with queue processing
- Add statistics endpoints with real-time data aggregation
- Add cover image upload functionality with processing
- Add overdue book management with notification system
- Add category management views with hierarchical structure
- Add rating and review system views
- Add advanced search views with filtering and sorting
- Update existing views to handle new fields and validations
- Add fine calculation logic to return book endpoint
- Add audit logging to all book operations
- Implement proper error handling and response formatting

### 6.4. Service Changes

**File: `books/services.py`**
- Add new service classes: `BookManagementService`, `ReservationService`, `FineCalculationService`, `ReportingService`, `ImageProcessingService`
- Update existing `BorrowingService` with enhanced functionality
- Add image processing logic with optimization
- Add fine calculation algorithms with policy management
- Add reservation queue management
- Add statistics calculation and aggregation
- Add audit trail functionality
- Add export and import functionality

### 6.5. URL Changes

**File: `books/urls.py`**
- Add new URL patterns for reservations, statistics, cover uploads, categories, and ratings
- Update existing patterns to handle new functionality
- Add nested URL patterns for fine operations and reservations
- Add bulk operation endpoints
- Add export endpoints for reports

### 6.6. Admin Changes

**File: `books/admin.py`**
- Register new models in Django admin with custom admin classes
- Add admin actions for reservation management and bulk operations
- Add filters and search for new fields
- Add fine management interface with bulk operations
- Add statistics dashboard in admin
- Add export functionality for book data
- Add audit trail display for book operations

### 6.7. Celery Tasks

**File: `books/tasks.py`** (NEW)
- Create task for overdue fine calculations with notifications
- Create task for reservation notifications and queue processing
- Create task for cover image processing and optimization
- Create task for cleanup operations (expired reservations, old audit logs)
- Create task for report data collection and aggregation
- Create task for fine payment reminders
- Create task for book rating statistics updates
- Create task for bulk book import/export operations

### 6.8. Middleware Changes

**File: `books/middleware.py`** (NEW)
- Create audit logging middleware for book operations
- Create fine calculation middleware for overdue books
- Create reservation queue middleware
- Create image processing middleware

---

## 7. Events (Optional)

-   **Publishes:**
    -   `book.cover.uploaded`: When a book cover is uploaded. Carries `book_id`, `image_url`, `file_size`.
    -   `book.rating.added`: When a book is rated. Carries `book_id`, `user_id`, `rating`, `review`.
    -   `book.reserved`: When a book is reserved. Carries `reservation_id`, `user_id`, `book_id`, `position_in_queue`.
    -   `book.available`: When a reserved book becomes available. Carries `book_id`, `reservation_ids`.
    -   `book.overdue`: When a book becomes overdue. Carries `record_id`, `days_overdue`, `fine_amount`.
    -   `book.damaged`: When a book is returned damaged. Carries `record_id`, `damage_level`, `damage_fine`.
    -   `fine.created`: When a fine is created for overdue book. Carries `fine_id`, `user_id`, `amount`.
    -   `reservation.fulfilled`: When a reservation is fulfilled. Carries `reservation_id`, `user_id`, `book_id`.

---

## 8. Integration Points

### 8.1. Users Module Integration
- Fine creation and management through user suspension
- Membership expiry validation for borrowing
- User activity tracking for borrowing operations
- Profile-based borrowing preferences

### 8.2. Reports Module Integration
- Borrowing statistics for weekly reports
- Fine statistics for financial reports
- Popular books and genres data
- Overdue book statistics and trends

### 8.3. Celery Tasks
- Automatic overdue fine calculations with notifications
- Reservation notification emails and queue processing
- Cover image processing and optimization
- Data cleanup operations and maintenance

### 8.4. External Services
- Cloud storage for book cover images
- Email service for notifications
- SMS service for urgent notifications
- Analytics service for book popularity tracking

---

## 9. Configuration Requirements

### 9.1. Settings Updates
- Fine calculation rates and policies (daily rate, maximum fine, grace period)
- Due date calculation rules (member vs admin, book type considerations)
- Reservation expiry settings and queue management
- Image upload configuration (size limits, formats, storage)
- Overdue notification settings and frequency
- Search and filtering configuration
- Rating system configuration

### 9.2. Environment Variables
- Fine calculation parameters and policies
- Image storage configuration (AWS S3, local storage)
- Email notification settings and templates
- Report generation settings and formats
- Search engine configuration
- Analytics service configuration

### 9.3. Database Configuration
- Indexes for book search queries (title, author, isbn, tags)
- Indexes for borrowing queries (user_id, status, due_date)
- Indexes for reservation queries (book_id, status, priority)
- Indexes for rating queries (book_id, user_id)
- Partitioning for large audit log tables

---

## 10. Testing Requirements

### 10.1. Unit Tests
- Fine calculation logic with various scenarios and policies
- Due date calculation with different user roles and book types
- Reservation queue management and priority calculation
- Image processing and optimization
- Rating system and statistics calculation
- Search functionality with multiple filters
- Category management with hierarchical structure

### 10.2. Integration Tests
- Fine creation from overdue returns with notifications
- Reservation fulfillment workflow with queue processing
- Report data collection and aggregation
- Image upload and processing pipeline
- Bulk book import/export operations
- Audit trail functionality
- Category management operations

### 10.3. API Tests
- All new endpoints with proper authentication and authorization
- Enhanced validation logic for new fields
- Permission testing for admin operations
- Error handling scenarios (invalid data, missing fields)
- Rate limiting and throttling for image uploads
- Bulk operation endpoints with proper validation
- Statistics and reporting endpoints with data accuracy

### 10.4. Performance Tests
- Book search performance with large datasets
- Fine calculation performance under load
- Reservation queue processing performance
- Image processing performance with various formats
- Statistics calculation performance
- Bulk operations performance
- Report generation performance

### 10.5. Security Tests
- Image upload security (file type validation, size limits)
- Fine manipulation prevention
- Reservation queue manipulation prevention
- Input validation and sanitization
- SQL injection prevention
- XSS protection in reviews and comments
- Access control for admin operations

---

## 11. Deployment Considerations

### 11.1. Database Migrations
- Careful migration strategy for adding new fields to Book model
- Data migration for existing books (default values, ISBN validation)
- Index creation for performance optimization
- Partitioning strategy for audit log tables

### 11.2. Background Tasks
- Celery worker configuration for image processing
- Task queue monitoring and alerting
- Failed task handling and retry logic
- Task scheduling for periodic operations

### 11.3. File Storage
- Book cover image storage configuration
- Image processing and optimization pipeline
- Backup and recovery procedures
- CDN integration for image delivery

### 11.4. Monitoring and Logging
- Fine calculation monitoring and alerting
- Reservation queue monitoring
- Image processing performance monitoring
- Search performance monitoring
- Error tracking and alerting
- Audit trail maintenance

---

## 12. Documentation Requirements

### 12.1. API Documentation
- Complete OpenAPI/Swagger documentation for all new endpoints
- Request/response examples with all new fields
- Error code documentation and handling
- Authentication and authorization details
- Rate limiting information for image uploads

### 12.2. User Documentation
- Book reservation process and queue management
- Rating and review system usage
- Advanced search and filtering guide
- Fine payment and extension procedures
- Category browsing and organization

### 12.3. Admin Documentation
- Enhanced book management procedures
- Reservation queue management
- Fine calculation and management
- Statistics and reporting tools
- Image upload and processing guidelines
- Category management procedures

---

## 13. Future Enhancements

### 13.1. Advanced Features
- Book recommendations engine
- Advanced analytics and insights
- Multi-language support for book metadata
- E-book integration
- Social features (reading lists, book clubs)
- Advanced notification system

### 13.2. Performance Optimizations
- Search engine optimization (Elasticsearch integration)
- Database query optimization and caching
- Background job optimization
- API response optimization
- Image delivery optimization

### 13.3. Security Enhancements
- Advanced rate limiting and DDoS protection
- Fraud detection for reservations
- Security audit logging
- Data encryption for sensitive information
- Privacy compliance features 