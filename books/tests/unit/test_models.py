import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from books.models import Book, BorrowRecord, Reservation, Fine

User = get_user_model()


class BookModelTest(TestCase):
    """
    Test case for the Book model.
    Tests field validations and model methods.
    """
    
    def setUp(self):
        """
        Set up test data for Book model tests.
        """
        self.book_data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'genre': 'Test Genre',
            'isbn': '1234567890123',
            'publication_date': timezone.now().date(),
            'cover_image_url': 'http://example.com/cover.jpg',
            'quantity': 5
        }
        
        self.book = Book.objects.create(**self.book_data)
    
    def test_book_creation(self):
        """
        Test that a book can be created with all required fields.
        """
        self.assertEqual(self.book.title, self.book_data['title'])
        self.assertEqual(self.book.author, self.book_data['author'])
        self.assertEqual(self.book.genre, self.book_data['genre'])
        self.assertEqual(self.book.isbn, self.book_data['isbn'])
        self.assertEqual(self.book.publication_date, self.book_data['publication_date'])
        self.assertEqual(self.book.cover_image_url, self.book_data['cover_image_url'])
        self.assertEqual(self.book.quantity, self.book_data['quantity'])
    
    def test_book_str_representation(self):
        """
        Test the string representation of a Book instance.
        """
        expected_str = f"{self.book.title} by {self.book.author}"
        self.assertEqual(str(self.book), expected_str)
    
    def test_book_optional_fields(self):
        """
        Test that a book can be created with optional fields as null.
        """
        book_with_optional_nulls = Book.objects.create(
            title='Optional Test Book',
            author='Optional Test Author',
            genre='Optional Test Genre',
            quantity=3
        )
        
        self.assertIsNone(book_with_optional_nulls.isbn)
        self.assertIsNone(book_with_optional_nulls.publication_date)
        self.assertIsNone(book_with_optional_nulls.cover_image_url)


class BorrowRecordModelTest(TestCase):
    """
    Test case for the BorrowRecord model.
    Tests field validations and model methods.
    """
    
    def setUp(self):
        """
        Set up test data for BorrowRecord model tests.
        """
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        # Create a test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Test Genre',
            quantity=5
        )
        
        # Create a test borrow record
        self.borrow_record = BorrowRecord.objects.create(
            user=self.user,
            book=self.book,
            status='PENDING'
        )
    
    def test_borrow_record_creation(self):
        """
        Test that a borrow record can be created with all required fields.
        """
        self.assertEqual(self.borrow_record.user, self.user)
        self.assertEqual(self.borrow_record.book, self.book)
        self.assertEqual(self.borrow_record.status, 'PENDING')
        self.assertIsNone(self.borrow_record.borrow_date)
        self.assertIsNone(self.borrow_record.due_date)
        self.assertIsNone(self.borrow_record.return_date)
    
    def test_borrow_record_str_representation(self):
        """
        Test the string representation of a BorrowRecord instance.
        """
        expected_str = f"{self.user.username} - {self.book.title} - {self.borrow_record.status}"
        self.assertEqual(str(self.borrow_record), expected_str)
    
    def test_borrow_record_status_choices(self):
        """
        Test that a borrow record can have different status values.
        """
        # Test APPROVED status
        self.borrow_record.status = 'APPROVED'
        self.borrow_record.borrow_date = timezone.now().date()
        self.borrow_record.due_date = timezone.now().date() + timedelta(days=14)
        self.borrow_record.save()
        
        self.assertEqual(self.borrow_record.status, 'APPROVED')
        self.assertIsNotNone(self.borrow_record.borrow_date)
        self.assertIsNotNone(self.borrow_record.due_date)
        
        # Test RETURNED status
        self.borrow_record.status = 'RETURNED'
        self.borrow_record.return_date = timezone.now().date()
        self.borrow_record.save()
        
        self.assertEqual(self.borrow_record.status, 'RETURNED')
        self.assertIsNotNone(self.borrow_record.return_date)
        
        # Test REJECTED status
        another_record = BorrowRecord.objects.create(
            user=self.user,
            book=self.book,
            status='REJECTED'
        )
        
        self.assertEqual(another_record.status, 'REJECTED')


class ReservationModelTest(TestCase):
    """
    Test case for the Reservation model.
    Tests field validations and model methods.
    """
    
    def setUp(self):
        """
        Set up test data for Reservation model tests.
        """
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        # Create a test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Test Genre',
            quantity=0  # Book is unavailable
        )
        
        # Create a test reservation
        self.reservation = Reservation.objects.create(
            user=self.user,
            book=self.book,
            status='PENDING',
            reservation_date=timezone.now().date()
        )
    
    def test_reservation_creation(self):
        """
        Test that a reservation can be created with all required fields.
        """
        self.assertEqual(self.reservation.user, self.user)
        self.assertEqual(self.reservation.book, self.book)
        self.assertEqual(self.reservation.status, 'PENDING')
        self.assertIsNotNone(self.reservation.reservation_date)
        self.assertFalse(self.reservation.notification_sent)
    
    def test_reservation_str_representation(self):
        """
        Test the string representation of a Reservation instance.
        """
        expected_str = f"{self.user.username} - {self.book.title} - {self.reservation.status}"
        self.assertEqual(str(self.reservation), expected_str)
    
    def test_reservation_status_choices(self):
        """
        Test that a reservation can have different status values.
        """
        # Test FULFILLED status
        self.reservation.status = 'FULFILLED'
        self.reservation.notification_sent = True
        self.reservation.save()
        
        self.assertEqual(self.reservation.status, 'FULFILLED')
        self.assertTrue(self.reservation.notification_sent)
        
        # Test CANCELLED status
        another_reservation = Reservation.objects.create(
            user=self.user,
            book=self.book,
            status='CANCELLED',
            reservation_date=timezone.now().date()
        )
        
        self.assertEqual(another_reservation.status, 'CANCELLED')


class FineModelTest(TestCase):
    """
    Test case for the Fine model.
    Tests field validations and model methods.
    """
    
    def setUp(self):
        """
        Set up test data for Fine model tests.
        """
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        # Create a test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Test Genre',
            quantity=5
        )
        
        # Create a test borrow record
        self.borrow_record = BorrowRecord.objects.create(
            user=self.user,
            book=self.book,
            status='RETURNED',
            borrow_date=timezone.now().date() - timedelta(days=20),
            due_date=timezone.now().date() - timedelta(days=6),
            return_date=timezone.now().date()
        )
        
        # Create a test fine
        self.fine = Fine.objects.create(
            borrow_record=self.borrow_record,
            user=self.user,
            amount=Decimal('3.00'),
            reason='Overdue return',
            status='PENDING',
            days_overdue=6
        )
    
    def test_fine_creation(self):
        """
        Test that a fine can be created with all required fields.
        """
        self.assertEqual(self.fine.borrow_record, self.borrow_record)
        self.assertEqual(self.fine.user, self.user)
        self.assertEqual(self.fine.amount, Decimal('3.00'))
        self.assertEqual(self.fine.reason, 'Overdue return')
        self.assertEqual(self.fine.status, 'PENDING')
        self.assertEqual(self.fine.days_overdue, 6)
    
    def test_fine_str_representation(self):
        """
        Test the string representation of a Fine instance.
        """
        expected_str = f"{self.user.username} - ${self.fine.amount} - {self.fine.status}"
        self.assertEqual(str(self.fine), expected_str)
    
    def test_fine_status_choices(self):
        """
        Test that a fine can have different status values.
        """
        # Test PAID status
        self.fine.status = 'PAID'
        self.fine.save()
        
        self.assertEqual(self.fine.status, 'PAID')
        
        # Test WAIVED status
        another_fine = Fine.objects.create(
            borrow_record=self.borrow_record,
            user=self.user,
            amount=Decimal('2.50'),
            reason='Overdue return',
            status='WAIVED',
            days_overdue=5
        )
        
        self.assertEqual(another_fine.status, 'WAIVED')
