# Books App

This app handles books and borrowing workflows with a 3-layer architecture:

- api layer
  - `api/views.py`: `BookViewSet` (CRUD with admin-only mutations), `BorrowViewSet` (borrow/return/approval/history), `FineViewSet` (list/retrieve/pay/waive)
  - `api/serializers.py`: `BookSerializer`, `BorrowRecordSerializer`, `FineSerializer`
  - `api_urls.py`: routers for `books`, `borrow`, and `fines`
- services layer
  - `services/book_service.py`: `BookService` (create/update/delete)
  - `services/borrow_service.py`: `BorrowService` (request, approve, reject, return)
  - `services/fine_service.py`: `FineService` (calculate overdue fine, pay, waive)
  - `services/__init__.py` and `services.py`: re-exports for compatibility
- data layer
  - `data/book_repository.py`, `data/borrow_repository.py`: ORM accessors
  - `data.py`: re-exports for compatibility

Models:
- `Book`: metadata + `available_copies` + new fields `isbn`, `publication_date`, `cover_image_url`
- `BorrowRecord`: status state machine (PENDING -> APPROVED -> RETURNED | REJECTED)
- `Fine`: tracks overdue fines for a `BorrowRecord` with fields: `amount`, `reason`, `status` (PENDING, PAID, WAIVED)

Permissions:
- `IsAdmin` guards book mutations and approval actions
- Auth required for listing, borrowing, and history
- Fines: list/retrieve are admin-only; pay allowed to the fine owner or admin; waive is admin-only

URLs (mounted under `/api/books/`):
- `books/` (GET list, GET detail; POST/PATCH/DELETE admin)
- `borrow/borrow/` (POST)
- `borrow/return/` (POST)
- `borrow/approvals/` (GET admin)
- `borrow/{id}/approve/` (PATCH admin)
- `borrow/{id}/reject/` (PATCH admin)
- `borrow/{id}/return/approve/` (PATCH admin)
- `borrow/history/` (GET)
- `fines/` (GET admin; optional `?status=` filter)
- `fines/{id}/` (GET admin)
- `fines/{id}/pay/` (POST member or admin)
- `fines/{id}/waive/` (POST admin)

Business logic notes:
- Returning a book after its due date automatically creates a `Fine` via `FineService.calculate_and_create_fine_if_overdue` invoked from `BorrowService.return_book`.
- `BookViewSet` supports search on `title`, `author`, `genre`, and `isbn`, plus simple ordering via the `ordering` query param.

Seed data:
- `management/commands/seed_data.py` now reads `isbn`, `publication_date`, and `cover_image_url` from `books.csv` and populates them on `Book` records.
