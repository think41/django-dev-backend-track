
# Module Specification: `[Books]`

**Version:** 1.0

**Author:** [Author Name]

**Date:** [Date]

---

## 1. Purpose and Responsibility

---Handles retrieval,addition,deletion of books related to a user

## 2. Dependencies

---

## 3. Data Models / Schema

---
Book Inventory:
    id
    status(borrowed/available)
    Title

Borrow History:
    user_id
    Book_id
    Borrowed At
    Due Date
    Status

## 4. API Endpoints
---
1./retrieve-available-books
2./add-book
3./delete-book
4./update-due-date
5./update-status

## 5. Services and Business Logic

1.add entry to the borrowed history table
2.delete a entry from the history table
3.update status entry 

