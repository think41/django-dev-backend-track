# Users App

This app implements the Users domain for the Library Management System using a 3-layer architecture:

- api layer: DRF viewsets/serializers and URL routing
  - `api/views.py`: `AuthViewSet` (register/login), `MembersViewSet` (admin-only user ops and history)
  - `api/serializers.py`: `RegisterSerializer`, `LoginSerializer`, `UserSerializer`
  - `api_urls.py`: includes routers for `auth` and `members`
- services layer: business logic orchestrating repositories and frameworks
  - `services/user_service.py`: `UserService` (register, approve_user, update_role, JWT tokens)
  - `services.py`: re-exports `UserService` for backward-compatible imports
- data layer: repositories that access the DB through ORM
  - `data/user_repository.py`: `UserRepository` (lookups, list)
  - `data.py`: re-exports `UserRepository` for backward-compatible imports

Other notable files:
- `models.py`: custom `User` model (UUID PK, roles: ADMIN/MEMBER) used as `AUTH_USER_MODEL`
- `management/commands/wait_for_db.py`: utility command for Compose startup

Why shims (re-export files) exist:
- To avoid breaking imports while adopting the 3-layer layout. Once references are updated across the codebase, the shim files (`services.py`, `data.py`, `api_views.py`) can be safely removed.

Permissions and auth:
- JWT via djangorestframework-simplejwt (configured in project settings)
- `IsAdmin` checks `request.user.role == 'ADMIN'` for admin-only endpoints

URLs (mounted under `/api/users/`):
- `auth/register/` (POST)
- `auth/login/` (POST)
- `members/` (GET list, GET detail)
- `members/{id}/approve-user/` (POST)
- `members/{id}/update-roles/` (POST)
- `members/{id}/borrow/` (GET)
- `members/{id}/borrow/{book_id}/` (GET)
