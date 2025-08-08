

## 1. Purpose and Responsibility

The Users module is responsible for managing user accounts in the Library Management System. There are two types of users: admin and member. Admins can approve member registrations and manage users through Django's built-in admin panel. Members can borrow books, and their borrowed books are tracked within the User model itself. 

---

## 3. Data Models / Schema

### User Model (extending Django's AbstractUser)
```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    borrowed_books = models.JSONField(default=list, blank=True)  # Array of borrowed book IDs with metadata
    # Inherits: username, password, date_joined from AbstractUser
   

---

## 4. API Endpoints

### Admin Endpoints (via Django Admin Panel)

Admins will use Django's built-in admin panel to:
- View and manage all users
- Approve/reject member registrations (change status from PENDING to ACTIVE)
- Update user details and permissions
- View borrowed books for each user

#### List All Users (API)
`/api/users/admin/`
- **Method:** `GET`
- **Permission:** `IsAdmin`
- **Response:**
  ```json
  [
    {
      "id": "integer",
      "username": "string",
      "email": "string",
      "role": "string",
      "status": "string",
      "date_joined": "datetime",
      "borrowed_books": "array"
    }
  ]
  ```

#### Approve Member Registration
`/api/users/admin/approve/{user_id}/`
- **Method:** `PATCH`
- **Permission:** `IsAdmin`
- **Description:** Approve a pending member registration

#### View All Borrow Records
`/api/users/admin/borrow-records/`
- **Method:** `GET`
- **Permission:** `IsAdmin`
- **Query Parameters:**
  - `status`: Filter by status (PENDING, APPROVED, REJECTED, RETURNED)
  - `user_id`: Filter by specific user
- **Description:** View and filter all borrow records across all users

#### Approve Borrow Request
`/api/users/admin/approve-borrow/{user_id}/{book_id}/`
- **Method:** `PATCH`
- **Permission:** `IsAdmin`
- **Description:** Approve a member's book borrowing request

#### Reject Borrow Request
`/api/users/admin/reject-borrow/{user_id}/{book_id}/`
- **Method:** `PATCH`
- **Permission:** `IsAdmin`
- **Description:** Reject a member's book borrowing request


### -------------------------------------User Profile Endpoints----------------------------------

#### Get User Profile
`/api/users/profile/`

Permission: `IsAuthenticated`
Description: Allows authenticated users to view their own profile information.

#### Update User Profile
`/api/users/profile/`
- **Method:** `PUT/PATCH`
- **Permission:** `IsAuthenticated`
- **Request Body:**
  ```json
  {
    "email": "string"
  }
  ```
- **Description:** Allows users to update their email address

### Member Borrowing Endpoints

#### Request to Borrow a Book
`/api/users/borrow/request/`
- **Method:** `POST`
- **Permission:** `IsAuthenticated` (Member only)
- **Request Body:**
  ```json
  {
    "book_id": "integer"
  }
  ```
- **Description:** Allows members to request borrowing a book

#### Return a Book
`/api/users/borrow/return/{book_id}/`
- **Method:** `PATCH`
- **Permission:** `IsAuthenticated` (Member only)
- **Description:** Allows members to return a borrowed book

#### View Borrowing History
`/api/users/borrow/history/`
- **Method:** `GET`
- **Permission:** `IsAuthenticated` (Member only)
- **Response:**
  ```json
  [
    {
      "book_id": "integer",
      "book_title": "string",
      "request_date": "datetime",
      "approval_date": "datetime",
      "return_date": "datetime",
      "due_date": "datetime",
      "status": "string"
    }
  ]
  ```
- **Description:** Allows members to view their borrowing history

---

## 5. Services and Business Logic

### User Management
- User registration creates users with PENDING status
- Admins approve registrations by changing status to ACTIVE
- Only ACTIVE users can borrow books

### Borrowing Logic
- Member's borrowed_books field stores array of borrowing records:
  ```json
  [
    {
      "book_id": 1,
      "request_date": "2025-01-15T10:30:00Z",
      "approval_date": "2025-01-15T14:20:00Z",
      "due_date": "2025-01-29T14:20:00Z",
      "return_date": null,
      "status": "APPROVED"
    }
  ]
  ```
- Status options: PENDING, APPROVED, REJECTED, RETURNED
- Admin approval updates book availability and adds approval_date
- Book return updates return_date and book availability
