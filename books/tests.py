from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Book, BorrowRecord

User = get_user_model()


class BookModelTest(TestCase):
    def test_create_book(self):
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Fiction',
            quantity=5
        )
        self.assertEqual(book.title, 'Test Book')
        self.assertEqual(book.quantity, 5)


class BorrowRecordModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Fiction',
            quantity=1
        )

    def test_create_borrow_record(self):
        record = BorrowRecord.objects.create(
            user=self.user,
            book=self.book
        )
        self.assertEqual(record.status, 'PENDING')
        self.assertEqual(record.user, self.user)
        self.assertEqual(record.book, self.book) 