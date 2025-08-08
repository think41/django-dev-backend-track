# Books App

This app handles books and borrowing workflows with a 3-layer architecture:

- api layer
  - `api/views.py`: `BookViewSet` (CRUD with admin-only mutations), `BorrowViewSet` (borrow/return/approval/history)
  - `api/serializers.py`: `BookSerializer`, `BorrowRecordSerializer`
  - `api_urls.py`: routers for `books` and `borrow`
- services layer
  - `services/book_service.py`: `BookService` (create/update/delete)
  - `services/borrow_service.py`: `BorrowService` (request, approve, reject, return)
  - `services.py`: re-exports for compatibility
- data layer
  - `data/book_repository.py`, `data/borrow_repository.py`: ORM accessors
  - `data.py`: re-exports for compatibility

Models:
- `Book`: metadata + `available_copies`
- `BorrowRecord`: status state machine (PENDING -> APPROVED -> RETURNED | REJECTED)

Permissions:
- `IsAdmin` guards book mutations and approval actions
- Auth required for listing, borrowing, and history

URLs (mounted under `/api/books/`):
- `books/` (GET list, GET detail; POST/PATCH/DELETE admin)
- `borrow/borrow/` (POST)
- `borrow/return/` (POST)
- `borrow/approvals/` (GET admin)
- `borrow/{id}/approve/` (PATCH admin)
- `borrow/{id}/reject/` (PATCH admin)
- `borrow/{id}/return/approve/` (PATCH admin)
- `borrow/history/` (GET)
