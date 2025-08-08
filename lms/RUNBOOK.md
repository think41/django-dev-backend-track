# LMS Backend Runbook

## Prerequisites
- Docker and Docker Compose installed

## First-time setup & run
```bash
docker compose up --build
```
This will:
1. Build the image (using uv to install dependencies)
2. Wait for the Postgres database to be healthy
3. Run `makemigrations` and `migrate`
4. Seed initial data from `data/users.csv` and `data/books.csv` (if present)
5. Start Django at `http://localhost:8000`

## Local development (optional)
- If you prefer running locally: create a `.env` or export `DATABASE_URL` pointed to your DB and run
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API base URLs
- API base: `/api/`
- Schema: `/api/schema/`
- Swagger UI: `/api/docs/`

## Ordered API walkthrough
Use Authorization: Bearer <access_token> header after login. Admin-only steps are marked.

1) Register a member
    - Method/Path: POST `/api/users/auth/register/`
    - Body:
      ```json
      {"username":"alice","email":"alice@example.com","password":"Passw0rd!","role":"MEMBER"}
      ```

2) Login as admin (seeded or superuser) to approve users [ADMIN]
    - Method/Path: POST `/api/users/auth/login/`
    - Body:
      ```json
      {"identifier":"admin","password":"<admin_password>"}
      ```
    - Copy `access` token from response.

3) Approve the new member [ADMIN]
    - Method/Path: POST `/api/users/members/{user_id}/approve-user/`

4) Member login to get token
    - Method/Path: POST `/api/users/auth/login/`
    - Body:
      ```json
      {"identifier":"alice","password":"Passw0rd!"}
      ```

5) List books
    - Method/Path: GET `/api/books/books/`

6) Create a book [ADMIN]
    - Method/Path: POST `/api/books/books/`
    - Body:
      ```json
      {"title":"Django Unleashed","author":"A. Author","genre":"Tech","isbn":"9780000000001","total_copies":5,"available_copies":5}
      ```

7) Member requests to borrow a book
    - Method/Path: POST `/api/books/borrow/borrow/`
    - Body:
      ```json
      {"book_id":"<book_uuid>"}
      ```

8) Admin views pending approvals [ADMIN]
    - Method/Path: GET `/api/books/borrow/approvals/`

9) Admin approves a borrow request [ADMIN]
    - Method/Path: PATCH `/api/books/borrow/{borrow_id}/approve/`

10) Member views their borrow history
     - Method/Path: GET `/api/books/borrow/history/`

11) Member initiates return
     - Method/Path: POST `/api/books/borrow/return/`
     - Body:
       ```json
       {"borrow_record_id":"<borrow_uuid>"}
       ```

12) Admin approves the return [ADMIN]
     - Method/Path: PATCH `/api/books/borrow/{borrow_id}/return/approve/`

13) Admin can inspect a user’s borrow history [ADMIN]
     - GET `/api/users/members/{user_id}/borrow/`
     - GET `/api/users/members/{user_id}/borrow/{book_id}/`

## Credentials
- Check `data/users.csv` for seeded admin/member credentials, or create an admin user via `createsuperuser`.

## Notes
- Custom user model: `users.User` with roles: `ADMIN`, `MEMBER`
- JWT auth via djangorestframework-simplejwt
- Filtering/search supported on books endpoints
