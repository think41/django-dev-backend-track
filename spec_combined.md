# Library Management System - Combined Specification

**Version:** 1.0

**Author:** System Architect

**Date:** 2025-08-08

---

## 1. Purpose and Responsibility

**Description:** The Library Management System is a Django-based REST API application that enables efficient management of books and user interactions in a library environment. It combines user management, authentication, and book catalog management with borrowing lifecycle tracking.

**Scope:**
-   **IN SCOPE:**
    -   User registration, authentication, and role-based access control
    -   Book inventory management (CRUD operations)
    -   Member book search and borrowing request workflows
    -   Admin approval/rejection of user registrations and borrow requests
    -   Tracking borrowing history and status management
    -   JWT-based authentication and authorization
-   **OUT OF SCOPE:**
    -   User profile management (password changes, email updates)
    -   Password reset functionality
    -   Book reservations for out-of-stock items
    -   Fines or penalties for overdue books
    -   Managing book categories as separate entities

The application implements a layered architecture ensuring separation of concerns and maintainable code structure.

---

## 2. Dependencies

-   **`django.contrib.auth`**: Used for the underlying user model and password management
-   **`djangorestframework`**: REST API framework for Django
-   **`djangorestframework-simplejwt`**: Required for generating and validating JWT tokens for authentication
-   **PostgreSQL**: Database for development and production
-   **`drf-yasg` or `drf-spectacular`**: API documentation generation

### JWT Payload Requirements
The JWT payload must include:
- `user_id`: The unique identifier of the user
- `role`: The user's role (`'admin'` or `'member'`)
- `exp`: The token's expiration timestamp

---

## 3. Data Models / Schema

### 3.1. `User` (Extends Django's AbstractUser)

**Description:** Represents a user of the system, who can be either an administrator or a member.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `username`      | `CharField(150)`                        | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. |
| `password`      | `CharField(128)`                        | The hashed password for the user account.                    |
| `email`         | `EmailField`                            | The user's email address. Must be unique.                    |
| `role`          | `CharField(10)`                         | The user's role. Choices are `admin` or `member`.            |
| `is_active`     | `BooleanField`                          | Designates whether this user should be treated as active. Unselect this instead of deleting accounts. Default: `False`. |
| `date_joined`   | `DateTimeField`                         | Timestamp of when the user registered.                       |

### 3.2. `Book`

**Description:** Represents a single book title in the library's collection.

| Field Name      | Data Type             | Description                                                  |
| --------------- | --------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                  | The primary key.                                             |
| `title`         | `CharField(255)`      | The title of the book.                                       |
| `author`        | `CharField(255)`      | The author of the book.                                      |
| `genre`         | `CharField(100)`      | The genre of the book.                                       |
| `quantity`      | `PositiveIntegerField`| The total number of copies of the book available to be borrowed. |
| `created_at`    | `DateTimeField`       | Timestamp of when the record was created.                    |
| `updated_at`    | `DateTimeField`       | Timestamp of the last update.                                |

### 3.3. `BorrowRecord`

**Description:** Tracks the status and history of a single borrowing transaction.

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

---

## 4. API Endpoints

**Base URLs:** `/api/users/` and `/api/books/`

### 4.1. Authentication & User Management Endpoints

#### User Registration and Login
-   **`POST /api/users/register/`**
    -   **Description:** Allows a new user to register for an account. The account is created as inactive and requires admin approval.
    -   **Permissions:** Public
    -   **Request Body:** `{ "username": "string", "password": "string", "email": "string" }`
    -   **Success Response (201 Created):** `{ "message": "Registration successful. Your account is pending approval from an administrator." }`
    -   **Failure Response (400 Bad Request):** If `username` or `email` already exist or data is invalid.

-   **`POST /api/users/login/`**
    -   **Description:** Authenticates an active user and provides JWT access and refresh tokens.
    -   **Permissions:** Public
    -   **Request Body:** `{ "username": "string", "password": "string" }`
    -   **Success Response (200 OK):** `{ "access": "string", "refresh": "string" }`
    -   **Failure Response (401 Unauthorized):** If credentials are invalid or the user's account (`is_active`) is `False`.

#### Admin User Management
-   **`GET /api/admin/users/`**
    -   **Description:** Retrieves a list of all users in the system.
    -   **Permissions:** Admin only
    -   **Query Params:** `?is_active=true/false` to filter users by their active status.
    -   **Success Response (200 OK):** `[ { "id": "int", "username": "string", "email": "string", "role": "string", "is_active": "boolean" }, ... ]`

-   **`PATCH /api/admin/users/{id}/approve/`**
    -   **Description:** Approves a user's registration by activating their account.
    -   **Permissions:** Admin only
    -   **Request Body:** (empty)
    -   **Success Response (200 OK):** `{ "message": "User account activated successfully." }`
    -   **Failure Response (404 Not Found):** If the user ID does not exist.

### 4.2. Book Management Endpoints

#### Book Catalog Operations
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

### 4.3. Book Borrowing Endpoints

#### Member Borrowing Operations
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

#### Admin Borrow Management
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

### 5.1. `UserRegistrationService`

-   **Purpose:** To handle the logic for creating a new user account.
-   **Methods:**
    -   `create_user(username, password, email)`: Hashes the provided password, sets the default `role` to `member` and `is_active` to `False`, and saves the new user instance.

### 5.2. `UserActivationService`

-   **Purpose:** To handle the logic for activating a user account.
-   **Methods:**
    -   `activate_user(user_id)`: Finds the user by their ID and sets their `is_active` status to `True`.

### 5.3. `BorrowingService`

-   **Purpose:** To manage the state transitions of a `BorrowRecord` and its side effects.
-   **Methods:**
    -   `request_borrow(user, book)`: Checks if the book is available. Creates a new `BorrowRecord` with `PENDING` status.
    -   `approve_request(borrow_record)`: Sets the record's status to `APPROVED`, sets the `borrow_date`, and decrements the associated book's `quantity`.
    -   `reject_request(borrow_record)`: Sets the record's status to `REJECTED`.
    -   `return_book(borrow_record)`: Sets the record's status to `RETURNED`, sets the `return_date`, and increments the associated book's `quantity`.

### 5.4. Application Architecture: Layered Architecture

#### 1. Presentation Layer (REST API)
- Django REST Framework views and serializers
- JWT authentication middleware
- Request/response handling and validation
- API endpoint routing

#### 2. Application Layer (Use Cases)
- User registration and approval workflows
- Book borrowing request workflows
- Search and filtering services
- Authentication and authorization services

#### 3. Domain Layer (Business Logic)
- User role management and validation
- Book availability tracking
- Borrowing rules and business validations
- Status management and state transitions

#### 4. Infrastructure Layer (Data Access)
- PostgreSQL database integration
- Django ORM models and migrations
- External service integrations
- File system operations

### 5.5. Key Business Rules

1. **User Management:**
   - New users register with `is_active=False` and require admin approval
   - Only active users can authenticate and receive JWT tokens
   - Default role for new users is `member`

2. **Book Management:**
   - Books can only be borrowed if `quantity > 0`
   - Book quantity is decremented upon borrow approval
   - Book quantity is incremented upon book return

3. **Borrowing Workflow:**
   - Members can only request books, not directly borrow them
   - All borrow requests start with `PENDING` status
   - Only admins can approve/reject borrow requests
   - Users cannot have duplicate pending requests for the same book
   - Books can only be returned by the borrowing user

4. **Authorization:**
   - JWT tokens are required for all authenticated endpoints
   - Admin-only endpoints require `role=admin`
   - Member operations require `is_active=True`

---

## 6. Events (Optional)

-   **Publishes:**
    -   `user.registered`: Published when a new user completes the registration form. Carries the `user_id` and `email`.
    -   `user.approved`: Published when an admin approves a user account. Carries the `user_id`.
    -   `borrow.request.created`: When a member requests a book. Carries `record_id`, `user_id`, `book_id`.
    -   `borrow.request.approved`: When an admin approves a request. Carries `record_id`.
    -   `borrow.request.rejected`: When an admin rejects a request. Carries `record_id`.
    -   `book.returned`: When a member returns a book. Carries `record_id`.