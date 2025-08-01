# Module Specification: `Users`

**Version:** 1.0

**Author:** Library System Team

**Date:** 2025-08-01

---

## 1. Purpose and Responsibility
Handles user registration, authentication (JWT), and role management (admin/member).

---

## 2. Dependencies
- Core module
- Django authentication system
- JWT libraries

---

## 3. Data Models / Schema
- **User**: Extends Django's user model, includes role (admin/member).
- **MemberProfile**: Additional info for members (if needed).

---

## 4. API Endpoints
- `POST /api/auth/register/` — Register new user
- `POST /api/auth/login/` — Obtain JWT token
- `GET /api/users/me/` — Get current user info

---

## 5. Services and Business Logic
- JWT authentication with user_id, role, and exp claims
- Role-based access: admin vs member
- Registration approval (admin)
