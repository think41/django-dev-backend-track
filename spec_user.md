USER ENDPOINTS

POST /auth/register/member
POST /auth/register/admin
POST /auth/login
GET /users/me
GET /users/approved
PUT /users/{id}/role
POST /users/{id}/approve
POST /users/{id}/disapprove
POST /auth/logout
DELETE /users/{id}

MIDDLEWARE

isAuth
isAdmin
isApproved
