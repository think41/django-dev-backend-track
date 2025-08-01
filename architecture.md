# 🏗️ Library Management System Architecture

## System Overview

The Library Management System is a RESTful backend application built with Django REST Framework, featuring JWT-based authentication, role-based access control, and PostgreSQL database integration.

## Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        C[Client Applications]
    end

    subgraph "API Gateway"
        AG[Django URL Router]
    end

    subgraph "Authentication Layer"
        JWT[JWT Authentication]
        PERM[Permission System]
    end

    subgraph "View Layer"
        UV[User Views]
        LV[Library Views]
        AV[Admin Views]
    end

    subgraph "Service Layer"
        US[User Service]
        LS[Library Service]
        BS[Borrow Service]
    end

    subgraph "Model Layer"
        UM[User Model]
        BM[Book Model]
        BR[BorrowRecord Model]
    end

    subgraph "Database Layer"
        PG[(PostgreSQL Database)]
    end

    subgraph "External Components"
        LOG[Logging System]
        EXC[Exception Handler]
    end

    C --> AG
    AG --> JWT
    JWT --> PERM
    PERM --> UV
    PERM --> LV
    PERM --> AV
    
    UV --> US
    LV --> LS
    AV --> BS
    
    US --> UM
    LS --> BM
    BS --> BR
    
    UM --> PG
    BM --> PG
    BR --> PG
    
    UV --> LOG
    LV --> LOG
    AV --> LOG
    
    UV --> EXC
    LV --> EXC
    AV --> EXC
```

## Component Architecture

### 1. Application Structure

```
lms_project/
├── lms_project/            # Django project configuration
│   ├── settings.py         # Environment configurations
│   ├── urls.py             # Root URL routing
│   └── wsgi.py/asgi.py     # WSGI/ASGI application
├── apps/                   # Modular application structure
│   ├── users/              # User management & authentication
│   └── library/            # Core library functionality
├── data/                   # CSV data files
└── requirements/           # Environment-specific dependencies
```

### 2. Request Flow Architecture

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant Auth
    participant View
    participant Service
    participant Model
    participant DB

    Client->>Router: HTTP Request
    Router->>Auth: Validate JWT Token
    Auth->>View: Authorized Request
    View->>Service: Business Logic Call
    Service->>Model: Database Operation
    Model->>DB: SQL Query
    DB-->>Model: Query Result
    Model-->>Service: Model Instance
    Service-->>View: Processed Data
    View-->>Client: JSON Response
```

## Core Components

### 3. Authentication & Authorization

```mermaid
graph LR
    subgraph "Authentication Flow"
        REG[Registration] --> APPROVAL[Admin Approval]
        APPROVAL --> LOGIN[Login]
        LOGIN --> JWT_TOKEN[JWT Token Generation]
    end

    subgraph "Authorization Roles"
        ADMIN[Admin Role]
        MEMBER[Member Role]
    end

    subgraph "Permissions"
        ADMIN --> ADMIN_PERMS[Book CRUD, User Management, Approvals]
        MEMBER --> MEMBER_PERMS[Search Books, Borrow/Return, View History]
    end
```

### 4. Data Models

```mermaid
erDiagram
    User {
        int id PK
        string username
        string email
        string password
        enum role
        boolean is_approved
        datetime created_at
        datetime updated_at
    }

    Book {
        int id PK
        string title
        string type
        text summary
        int total_copies
        int remaining_copies
        json reviews
        datetime created_at
        datetime updated_at
    }

    BorrowRecord {
        int id PK
        int user_id FK
        int book_id FK
        datetime borrow_date
        datetime return_date
        enum status
        datetime created_at
        datetime updated_at
    }

    User ||--o{ BorrowRecord : creates
    Book ||--o{ BorrowRecord : borrowed_in
```

### 5. API Endpoints Architecture

```mermaid
graph TB
    subgraph "Authentication Endpoints"
        AUTH_REG[POST /register/]
        AUTH_LOGIN[POST /login/]
        AUTH_REFRESH[POST /token/refresh/]
    end

    subgraph "Member Endpoints"
        MEMBER_SEARCH[GET /books/search/]
        MEMBER_BORROW[POST /books/borrow/]
        MEMBER_RETURN[POST /books/return/]
        MEMBER_HISTORY[GET /borrow-history/]
    end

    subgraph "Admin Endpoints"
        ADMIN_BOOKS[CRUD /admin/books/]
        ADMIN_USERS[GET /admin/users/]
        ADMIN_APPROVE_USER[POST /admin/users/approve/]
        ADMIN_BORROW_REQUESTS[GET /admin/borrow-requests/]
        ADMIN_APPROVE_BORROW[POST /admin/borrow-requests/approve/]
        ADMIN_REJECT_BORROW[POST /admin/borrow-requests/reject/]
    end
```

### 6. Service Layer Architecture

```mermaid
graph TB
    subgraph "User Service"
        US_REG[User Registration]
        US_AUTH[Authentication]
        US_APPROVAL[User Approval]
    end

    subgraph "Library Service"
        LS_SEARCH[Book Search]
        LS_CRUD[Book CRUD Operations]
        LS_INVENTORY[Inventory Management]
    end

    subgraph "Borrow Service"
        BS_REQUEST[Borrow Request]
        BS_APPROVAL[Borrow Approval]
        BS_RETURN[Book Return]
        BS_HISTORY[Borrow History]
    end
```

## Technology Stack

### Backend Framework
- **Django 5.2+**: Web framework
- **Django REST Framework**: API development
- **djangorestframework-simplejwt**: JWT authentication

### Database
- **PostgreSQL**: Primary database with ACID compliance
- **Docker**: Database containerization

### Additional Components
- **Custom Exception Handling**: Centralized error management
- **Logging System**: Application monitoring and debugging
- **Environment Configuration**: Development/Production separation
- **API Documentation**: drf-yasg or drf-spectacular

## Deployment Architecture


```mermaid
graph TB
    subgraph "Development Environment"
        DEV_APP[Django Development Server]
        DEV_DB[PostgreSQL Container]
    end

    subgraph "Production Environment"
        PROD_APP[Django Application]
        PROD_DB[(PostgreSQL Database)]
        PROD_WEB[Web Server]
    end

    subgraph "Monitoring & Logging"
        LOG_FILE[Application Logs]
        MONITORING[System Monitoring]
    end
```

## Security Considerations

- JWT-based stateless authentication
- Role-based access control (RBAC)
- Input validation through DRF serializers
- SQL injection prevention via Django ORM
- CSRF protection for web interfaces
- Environment-based configuration management

## Scalability Features

- Modular app structure for easy feature addition
- Service layer separation for business logic
- Database indexing for performance optimization
- Stateless JWT authentication for horizontal scaling
- Docker containerization for deployment flexibility

## Layer Explanation

### 1. **View Layer** (Django Views/ViewSets)
The view layer handles HTTP requests and responses. It's the controller in the MVC pattern.

**Components:**
- **User Views**: Handle authentication endpoints (register, login, token refresh)
- **Library Views**: Handle book-related operations (search, list, retrieve)
- **Admin Views**: Handle administrative operations (user approval, book management)

**Responsibilities:**
- Receive HTTP requests from the URL router
- Validate request data using serializers
- Call appropriate service layer methods
- Format and return HTTP responses
- Handle pagination, filtering, and sorting

### 2. **Client Layer**
External applications that consume the API.

**Examples:**
- Web frontend (React, Vue, Angular)
- Mobile applications (iOS, Android)
- Third-party integrations
- API testing tools (Postman, curl)

### 3. **API Gateway Layer** (Django URL Router)
Routes incoming requests to appropriate views.

**Responsibilities:**
- URL pattern matching
- Request routing to correct view functions
- URL parameter extraction
- Middleware execution order

### 4. **Authentication Layer**
Handles security and access control.

**Components:**
- **JWT Authentication**: Validates JWT tokens in request headers
- **Permission System**: Checks user roles and permissions (ADMIN vs MEMBER)

**Flow:**
```
Request → JWT Token Validation → Permission Check → View Access
```

### 5. **Service Layer** (Business Logic)
Contains complex business rules and operations.

**Components:**
- **User Service**: User registration, approval workflows
- **Library Service**: Book inventory management, search logic
- **Borrow Service**: Borrowing rules, due date calculations, availability checks

**Why Separate?**
- Keeps views thin and focused
- Reusable business logic
- Easier testing
- Clear separation of concerns

### 6. **Model Layer** (Django ORM Models)
Defines data structure and database operations.

**Components:**
- **User Model**: User data, roles, authentication
- **Book Model**: Book information, inventory tracking
- **BorrowRecord Model**: Borrowing transactions, status tracking

**Responsibilities:**
- Database schema definition
- Data validation
- Relationship management
- Query optimization

### 7. **Database Layer**
Physical data storage using PostgreSQL.

**Features:**
- ACID compliance
- Relational data integrity
- Query optimization
- Backup and recovery

### 8. **External Components**

#### Logging System
- Captures application events
- Error tracking and debugging
- Performance monitoring
- Audit trails

#### Exception Handler
- Centralized error handling
- Consistent error responses
- Error logging and notification
- User-friendly error messages

## Layer Interaction Flow

```
Client Request
    ↓
API Gateway (URL Routing)
    ↓
Authentication (JWT + Permissions)
    ↓
View Layer (Request/Response Handling)
    ↓
Service Layer (Business Logic)
    ↓
Model Layer (Data Operations)
    ↓
Database Layer (Data Storage)
```

## Benefits of This Architecture

1. **Separation of Concerns**: Each layer has distinct responsibilities
2. **Maintainability**: Changes in one layer don't affect others
3. **Testability**: Each layer can be tested independently
4. **Scalability**: Easy to scale individual components
5. **Reusability**: Service layer logic can be reused across views
6. **Security**: Centralized authentication and authorization

This layered architecture follows Django best practices and enterprise-level application design patterns.