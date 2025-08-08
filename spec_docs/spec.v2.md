# Version: 2.0

# Author: Ojas Aklecha

# Date: 08/08/2025

---

# Module Specification: `Books` (v2 Enhancements)

## 1. Purpose and Responsibility

This document outlines the version 2.0 enhancements for the `Books` module. The key changes include an enhanced data model for books and the introduction of a fine management system for overdue books.

## 2. Dependencies

No new major dependencies are expected for these enhancements.

## 3. Data Models / Schema

### `Book` Model (Enhancement)

The `Book` model will be updated to include a field for the cover image URL. The `isbn` and `publication_date` fields already exist and will be populated by the updated import script.

| Field           | Type     | Description                  |
|-----------------|----------|------------------------------|
| ...             | ...      | ...                          |
| cover_image_url | URLField | URL to the book's cover image. |
| ...             | ...      | ...                          |

### `Fine` Model (New)

A new model to track fines associated with overdue borrow records. This will likely reside within the `apps/books` app.

| Field         | Type                | Description                               |
|---------------|---------------------|-------------------------------------------|
| id            | UUID                | Primary Key                               |
| borrow_record | ForeignKey(BorrowRecord) | The associated borrow record.             |
| amount        | DecimalField        | The fine amount.                          |
| reason        | String              | Reason for the fine (e.g., "OVERDUE").    |
| status        | ENUM("PENDING", "PAID", "WAIVED") | The current status of the fine.           |
| created_at    | DateTime            | Timestamp of creation.                    |
| updated_at    | DateTime            | Timestamp of last update.                 |

## 4. API Endpoints (Implemented)

### Books
- CRUD: `/api/books/` (list, retrieve, create [ADMIN], update [ADMIN], delete [ADMIN])
- Search/filter parameters on list: `q`, `title`, `author`, `genre`, `ordering`
- Fields include: `isbn`, `publication_date`, `cover_image_url`

### Borrow
- Request borrow: `POST /api/borrow/borrow/`
- Approvals list [ADMIN]: `GET /api/borrow/approvals/`
- Approve [ADMIN]: `PATCH /api/borrow/{borrow_id}/approve/`
- Reject [ADMIN]: `PATCH /api/borrow/{borrow_id}/reject/`
- Return: `POST /api/borrow/return/`
- Return approve [ADMIN]: `PATCH /api/borrow/{borrow_id}/return/approve/`
- History (member): `GET /api/borrow/history/`
- Records [ADMIN]: `GET /api/borrow/records/?status=`

### Fines
- List [ADMIN]: `GET /api/fines/?status=`
- Retrieve [ADMIN]: `GET /api/fines/{fine_id}/`
- Pay [MEMBER/ADMIN]: `POST /api/fines/{fine_id}/pay/`
- Waive [ADMIN]: `POST /api/fines/{fine_id}/waive/`

## 5. Services and Business Logic

### `BookService`
- The `add_book` and `update_book` methods will be updated to handle the `cover_image_url` field.

### `FineService` (New)
- **`calculate_and_create_fine_if_overdue(borrow_record)`**: Checks if a returned book is overdue based on a defined policy (e.g., borrowed for more than X days) and creates a `Fine` record if necessary.
- **`pay_fine(fine)`**: Logic to handle fine payment confirmation.
- **`waive_fine(fine)`**: Logic to handle waiving a fine.

### `BorrowService`
- The `return_book` or `return_approve` service method will be updated to call `FineService.calculate_and_create_fine_if_overdue` when a book return is processed.

### Data Import Script
- The `seed_data` management command populates `isbn`, `publication_date`, and `cover_image_url` when provided in CSV.

## 6. Ordered API Walkthrough
1) Register member: `POST /api/users/auth/register/`
2) Admin login: `POST /api/users/auth/login/`
3) Approve member [ADMIN]: `POST /api/users/members/{user_id}/approve-user/`
4) Member login: `POST /api/users/auth/login/`
5) List/Search books: `GET /api/books/`
6) Create/Update/Delete book [ADMIN]: `POST|PATCH|DELETE /api/books/{id}/`
7) Borrow request: `POST /api/borrow/borrow/`
8) Approvals list [ADMIN]: `GET /api/borrow/approvals/`
9) Approve/Reject [ADMIN]: `PATCH /api/borrow/{borrow_id}/approve|reject/`
10) Return: `POST /api/borrow/return/`
11) Return approve [ADMIN]: `PATCH /api/borrow/{borrow_id}/return/approve/`
12) Fines (Admin listing): `GET /api/fines/?status=`
13) Pay/Waive fines: `POST /api/fines/{fine_id}/pay|waive/`