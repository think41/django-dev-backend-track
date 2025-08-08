from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User


class UsersFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create an admin user
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            role=User.Role.ADMIN,
            is_active=True,
        )

    def auth(self, user: User) -> APIClient:
        client = APIClient()
        # Obtain JWT via login endpoint
        login_url = reverse("login")
        resp = client.post(login_url, {"username": user.username, "password": "adminpass"}, format="json")
        self.assertEqual(resp.status_code, 200, resp.content)
        token = resp.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def test_register_then_admin_approves_then_user_can_login(self):
        # Register a new member
        register_url = reverse("register")
        resp = self.client.post(
            register_url,
            {"username": "member1", "email": "member1@example.com", "password": "memberpass123"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        created_user = User.objects.get(username="member1")
        self.assertFalse(created_user.is_active)
        self.assertEqual(created_user.role, User.Role.MEMBER)

        # Member cannot login before approval
        login_url = reverse("login")
        resp = self.client.post(
            login_url, {"username": "member1", "password": "memberpass123"}, format="json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("not approved", str(resp.data["non_field_errors"][0]).lower())

        # Admin lists inactive users
        admin_client = self.auth(self.admin)
        users_list_url = reverse("admin-users")
        resp = admin_client.get(users_list_url + "?is_active=false")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(u["username"] == "member1" for u in resp.json()))

        # Admin approves the user
        approve_url = reverse("admin-users-approve", kwargs={"pk": created_user.id})
        resp = admin_client.patch(approve_url, {}, format="json")
        self.assertEqual(resp.status_code, 200)
        created_user.refresh_from_db()
        self.assertTrue(created_user.is_active)

        # Now user can login and receive JWT tokens
        resp = self.client.post(
            login_url, {"username": "member1", "password": "memberpass123"}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

