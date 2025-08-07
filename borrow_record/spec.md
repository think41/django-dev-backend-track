# Module Specification: borrow_record

**Version:** 1.0

**Author:** Aviroop

**Date:** 07/08/2025

---

## 1. Purpose and Responsibility

The borrow_record module manages the borrowing lifecycle of books in the library management system. It handles borrow requests, approvals, returns, and tracks the status of all book borrows. This module coordinates between users and books to maintain accurate borrowing records and enforce borrowing rules.

---

## 2. Dependencies

- Django ORM for database operations
- Django REST Framework for API endpoints
- Auth module for user authentication and role management
- User module for user model references
- Books module for book availability and management

---

## 3. Data Models / Schema

**BorrowRecord Model:**
- id: Primary key (auto-generated)
- user: ForeignKey to User (required)
- book: ForeignKey to Book (required)
- status: CharField (choices: 'PENDING', 'APPROVED', 'REJECTED', 'RETURNED', default='PENDING')
- request_date: DateTimeField (auto_now_add=True)
- approved_date: DateTimeField (nullable)
- borrowed_date: DateTimeField (nullable)
- due_date: DateTimeField (nullable)
- returned_date: DateTimeField (nullable)
- approved_by: ForeignKey to User (nullable, for admin who approved)
- notes: TextField (nullable, for admin notes)

---

## 4. API Endpoints

**GET /api/borrow-records/**
- Purpose: List borrow records with filtering
- Access: Admin (all records), Member (own records)
- Query params: status, user_id, book_id
- Response: List of borrow record objects

**POST /api/borrow-records/**
- Purpose: Create borrow request
- Access: Members only
- Request body: book_id
- Response: Created borrow record object

**GET /api/borrow-records/{id}/**
- Purpose: Get specific borrow record details
- Access: Record owner or admin
- Response: Single borrow record object

**PUT /api/borrow-records/{id}/approve/**
- Purpose: Approve borrow request (admin only)
- Access: Admin only
- Request body: due_date, notes (optional)
- Response: Updated borrow record object

**PUT /api/borrow-records/{id}/reject/**
- Purpose: Reject borrow request (admin only)
- Access: Admin only
- Request body: notes (optional)
- Response: Updated borrow record object

**PUT /api/borrow-records/{id}/return/**
- Purpose: Return borrowed book
- Access: Record owner or admin
- Response: Updated borrow record object

**GET /api/borrow-records/my-borrows/**
- Purpose: Get current user's borrow history
- Access: Authenticated users
- Response: List of user's borrow records

---

## 5. Services and Business Logic

**BorrowRecordService:**
- def create_borrow_request(user_id, book_id): Creates new borrow request with validation
- def approve_borrow_request(record_id, admin_id, due_date): Approves request and updates book availability
- def reject_borrow_request(record_id, admin_id, notes): Rejects request with optional notes
- def return_book(record_id): Processes book return and updates availability
- def get_user_borrow_history(user_id): Retrieves user's complete borrow history
- def get_pending_requests(): Gets all pending borrow requests for admin review

**Business Rules:**
- Members can only request books that are available (available_copies > 0)
- Users cannot have multiple active borrows of the same book
- Only admins can approve or reject borrow requests
- Book availability is automatically updated when requests are approved/returned
- Due dates are set by admins during approval
- Returned books automatically update book availability count 