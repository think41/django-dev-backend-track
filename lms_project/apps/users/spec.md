# Module Specification: `users`

**Version:** 1.0

**Author:** Sherbin S

**Date:** 01-08-2025

---

## 1. Purpose and Responsibility
The `users` module is responsible for managing user accounts, including registration,login, and profile management. It provides endpoints for user creation, login, and user data retrieval

---

## 2. Dependencies

asgiref<br />
Django<br />
psycopg2-binary<br />
sqlparse<br />
tzdata<br />
djangorestframework<br />

---

## 3. Data Models / Schema

**Class Users**:<br />
    id<br />
    username <br />
    password <br />
    created_at<br />
    updated_at  <br />
    is_active<br />
    role
---

## 4. API Endpoints
### User Registration
Method: POST auth/register/<br />
Description: Registers a new user with a username and password.<br />

Request Body:
```json
{
    "username": "string",
    "password": "string"
}
```
Method: POST auth/login/<br />
Description: Authenticates a user and returns a token.<br />
Request Body:
```json
{
    "username": "string",
    "password": "string"
}
```
Method: GET auth/user/{id}<br />
Description: Retrieves user details by ID.<br />
Request Parameters:
```json
{
    "id": "integer"
}
```
---

## 5. Services and Business Logic

# UserService
The `UserService` class handles user-related operations such as registration, login, and fetching user details. It interacts with the `Users` model to perform CRUD operations.


