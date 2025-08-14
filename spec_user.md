# Module Specification: `[User]`

**Version:** 1.0

**Author:** [Author Name]

**Date:** [Date]

---

## 1. Purpose and Responsibility

---Handles user registration,login

## 2. Dependencies

---
Authentication with JWT token

## 3. Data Models / Schema

---
user data table:
    username
    id
    created_at
    role(admin,member)
    updated_at


## 4. API Endpoints

---
1./register
2./login

## 5. Services and Business Logic

1.Register the user/admin
2.Get user related profile info
3.Login the user/admin
