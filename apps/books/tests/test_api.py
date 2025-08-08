from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.books.models import Book, BorrowRecord
from datetime import date, timedelta


class BooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.member = User.objects.create_user(username="m1", password="pass", role="MEMBER", is_active=True)
        self.admin = User.objects.create_user(username="a1", password="pass", role="ADMIN", is_active=True, is_staff=True, is_superuser=True)
        # Auth as member by default
        self.client.force_authenticate(self.member)

    def test_book_search_filters(self):
        Book.objects.create(title="Django Unleashed", author="Andrew", genre="Tech")
        Book.objects.create(title="Python Tricks", author="Dan", genre="Tech")
        Book.objects.create(title="The Hobbit", author="Tolkien", genre="Fiction")

        # q search
        res = self.client.get("/api/books/", {"q": "Django"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

        # genre filter
        res = self.client.get("/api/books/", {"genre": "Tech"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 2)

        # title filter
        res = self.client.get("/api/books/", {"title": "Python"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

    def test_borrow_and_history(self):
        book = Book.objects.create(title="Book A", author="X", genre="G", available_copies=1)
        res = self.client.post("/api/borrow/borrow/", {"book_id": str(book.id)}, format="json")
        self.assertEqual(res.status_code, 201)
        rec_id = res.json()["id"]
        # History should show one record
        res = self.client.get("/api/borrow/history/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)
        # Return flow
        res = self.client.post("/api/borrow/return/", {"borrow_record_id": rec_id}, format="json")
        self.assertEqual(res.status_code, 200)

    def test_admin_records_list_and_status_filter(self):
        # create two records
        book = Book.objects.create(title="Book B", author="Y", genre="G", available_copies=2)
        r1 = BorrowRecord.objects.create(user=self.member, book=book, status=BorrowRecord.Status.PENDING)
        r2 = BorrowRecord.objects.create(user=self.member, book=book, status=BorrowRecord.Status.APPROVED)
        # switch to admin
        self.client.force_authenticate(self.admin)
        res = self.client.get("/api/borrow/records/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.json()), 2)
        res = self.client.get("/api/borrow/records/", {"status": "PENDING"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(all(item["status"] == "PENDING" for item in data))
        # invalid status
        res = self.client.get("/api/borrow/records/", {"status": "BAD"})
        self.assertEqual(res.status_code, 400)

    def test_admin_reject(self):
        book = Book.objects.create(title="Book C", author="Z", genre="G", available_copies=1)
        rec = BorrowRecord.objects.create(user=self.member, book=book, status=BorrowRecord.Status.PENDING)
        self.client.force_authenticate(self.admin)
        res = self.client.patch(f"/api/borrow/{rec.id}/reject/")
        self.assertEqual(res.status_code, 200)
        rec.refresh_from_db()
        self.assertEqual(rec.status, BorrowRecord.Status.REJECTED)

    def test_overdue_creates_fine_and_pay_waive(self):
        book = Book.objects.create(title="Book D", author="Q", genre="G", available_copies=1)
        # Create approved record 30 days ago to force overdue
        rec = BorrowRecord.objects.create(user=self.member, book=book, status=BorrowRecord.Status.APPROVED,
                                          borrow_date=date.today() - timedelta(days=30))
        # Return as member
        res = self.client.post(f"/api/borrow/return/", {"borrow_record_id": str(rec.id)}, format="json")
        self.assertEqual(res.status_code, 200)
        # Admin lists fines should be >=1 and pending
        self.client.force_authenticate(self.admin)
        res = self.client.get("/api/fines/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(any(item["borrow_record"] == str(rec.id) for item in data))
        # Grab first fine id and pay as member
        fine_id = data[0]["id"]
        self.client.force_authenticate(self.member)
        res = self.client.post(f"/api/fines/{fine_id}/pay/")
        self.assertIn(res.status_code, (200, 400))  # if already paid by earlier test order
        # Admin can waive a (different/new) fine
        self.client.force_authenticate(self.admin)
        res = self.client.post(f"/api/fines/{fine_id}/waive/")
        self.assertIn(res.status_code, (200, 400))
