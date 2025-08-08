
**Version:** 1.0

**Author:** Ojas Aklecha

**Date:** 01/08/2025

---

# Module Specification: `Auth`

## 1. Purpose and Responsibility

The purpose of this module is to provide authentication and authorization services for the library management system. It will handle user registrations and logins. 

It will handle user roles and authorisation and the permissions they will get. Either be the normal member or the admin.

## 2. Dependencies

djangorestframework-simplejwt

## 3. Data Models / Schema

| Field       | Type      |
|-------------|-----------|
| id          | UUID      |
| username    | String    |
| email       | String    |
| password    | String    |
| role        | String    |
| is_active   | Boolean   |
| created_at  | DateTime  |
| updated_at  | DateTime  |

## 4. API Endpoints

### Auth
- 1. /auth/register - Register api registers the new user. By default the user will be in-active.
- 2. /auth/login - Login api logs in the existing users. Here we filters based upon the permissions users have. eg. admin or member.
- 3. /auth/logout - Logout api logs out the user.

### Members
- 4. /members/update-roles - Update roles api updates the roles of the user.
- 5. /members/approve-user - Approve user is the admin only api which will approve the user registration and mark the user active.
- 6. /members/users - This will return all the users.
- 7. /members/user/<user_id> - This will return the user details.
- 8. /members/user/<user_id>/borrow - This will return the borrow history of the user.
- 9. /members/user/<user_id>/borrow/<book_id> - This will specific book borrowed by the user.

## 5. Services and Business Logic

- 1. Register - Takes username, email, password and role as input and registers the user. By default the user will be in-active. Checks if user already exists or not. If yes then return appropriate response else create the user. 
- 2. Login - Takes username or email and password as an input and logs in the user. Checks if user exists or the inputted details is correct or not. If yes then generates a JWT token for the user session and returns the token. If the user is not approved then it will show the basic message as user not active ( along with the jwt token ) and if the user is approved then it will send active user along with the jwt token.
- 3. Logout - Takes JWT token as an input and logs out the user. Checks if the token is valid or not. If yes then logs out the user and returns appropriate response.
- 4. Update Roles - This changes the user role from member->admin or admin->member. This is only for admin.
- 5. Approve User - Takes user id as an input and approves the user. This is only for admin.
- 6. Users - This returns all the users.
- 7. User - This returns the user details.
- 8. User Borrow History - This returns all the borrow history of the user.
- 9. User Borrow History - This returns the borrow history of the specific book by the user.

# Module Specification: `Books`

---

## 1. Purpose and Responsibility

This module defines the functionality of the books. All the search books, borrow books, return books, etc. are handled here.

## 2. Dependencies

django_filters
django-rest-framework


## 3. Data Models / Schema

| Field              | Type     |
|--------------------|----------|
| id                 | UUID     |
| title              | String   |
| author             | String   |
| genre              | String   |
| isbn               | String   |
| publisher          | String   |
| publication_date   | DateTime |
| available_copies   | Integer  |
| created_at         | DateTime |
| updated_at         | DateTime |

| Field        | Type                                                     |
|--------------|----------------------------------------------------------|
| id           | UUID                                                     |
| user_id      | UUID                                                     |
| book_id      | UUID                                                     |
| borrow_date  | DateTime                                                 |
| return_date  | DateTime                                                 |
| status       | ENUM("PENDING", "APPROVED", "REJECTED", "RETURN_PENDING", "RETURNED") |
| created_at   | DateTime                                                 |
| updated_at   | DateTime                                                 |

## 4. API Endpoints

### Books
- 1. /books/add - This will add a new book. ( admin )
- 2. /books/update - This will update the book. ( admin )
- 3. /books/delete - This will delete the book. ( admin )
- 4. /books/<book_id> - This will return the book details. ( user )
- 5. /books - This will return all the books. ( user )
- 6. /books/search - This will return the books based upon the search query. ( user )

### Borrow
- 1. /borrow/<book_id> - This will borrow the book by the bookid. ( user )
- 2. /borrow/return/<book_id> - This will return the book by the bookid. ( user )
- 3. /borrow/approval/<book_id> - This will approve or reject the borrow request. ( admin )
- 4. /borrow/approvals - This will return all the borrow approvals. ( admin )
- 5. /borrow/return/approval/<book_id> - This will approve/reject and process the return request. ( admin )
- 6. /borrow/history - This will return the borrow history of the user. ( user )
- 7. /borrow/history/<book_id> - This will return the borrow history of the user for a specific book. ( admin )

## 5. Services and Business Logic

- 1. Add Book - This will add a new book. ( admin )
- 2. Update Book - This will update the book. ( admin )
- 3. Delete Book - This will delete the book. ( admin )
- 4. Get Book - This will return the book details. ( user )
- 5. Get Books - This will return all the books. ( user )
- 6. Search Books - This will return the books based upon the search query. ( user )
- 7. Borrow Book - This will borrow the book by the bookid. ( user )
- 8. Return Book - This will return the book by the bookid. ( user )
- 9. Approve Borrow - This will approve or reject the borrow request. ( admin )
- 10. Get Borrow Approvals - This will return all the borrow approvals. ( admin )
- 11. Approve Return - This will approve/reject and process the return request. ( admin )
- 12. Get Borrow History - This will return the borrow history of the user. ( user )
- 13. Get Borrow History for Book - This will return the borrow history of the user for a specific book. ( admin )