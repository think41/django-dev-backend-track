from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User
from books.models import Book, BorrowRecord


class BooksFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Admin and approved member
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            role=User.Role.ADMIN,
            is_active=True,
        )
        self.member = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="memberpass",
            role=User.Role.MEMBER,
            is_active=True,
        )

    def auth(self, username: str, password: str) -> APIClient:
        client = APIClient()
        login_url = reverse("login")
        resp = client.post(login_url, {"username": username, "password": password}, format="json")
        assert resp.status_code == 200, resp.content
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
        return client

    def test_book_crud_and_borrow_return_flow(self):
        admin_client = self.auth("admin", "adminpass")
        member_client = self.auth("member", "memberpass")

        # Admin creates a book
        list_url = reverse("books-list-create")
        resp = admin_client.post(
            list_url,
            {"title": "1984", "author": "George Orwell", "genre": "Dystopian", "quantity": 2},
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        book_id = resp.data["id"]

        # Member lists and searches books
        resp = member_client.get(list_url + "?search=1984")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(b["id"] == book_id for b in resp.json()))

        # Member requests to borrow
        borrow_url = reverse("books-borrow")
        resp = member_client.post(borrow_url, {"book_id": book_id}, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        record_id = resp.data["id"]
        self.assertEqual(resp.data["status"], BorrowRecord.Status.PENDING)

        # Admin approves
        approve_url = reverse("admin-borrow-approve", kwargs={"pk": record_id})
        resp = admin_client.patch(approve_url, {}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], BorrowRecord.Status.APPROVED)

        # Member returns the book
        return_url = reverse("books-return")
        resp = member_client.post(return_url, {"borrow_record_id": record_id}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], BorrowRecord.Status.RETURNED)

        # Quantity should be decremented then incremented back
        resp = member_client.get(reverse("books-rud", kwargs={"pk": book_id}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["quantity"], 2)

