import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from books.models import Book, BorrowRecord, Reservation, Fine
from books.serializers import (
    BookSerializer,
    BorrowRecordSerializer,
    AdminBorrowRecordSerializer,
    UserBriefSerializer,
    BookBriefSerializer,
    ReservationSerializer,
    FineSerializer,
    AdminFineSerializer
)

User = get_user_model()


class BookSerializerTest(TestCase):
    """
    Test case for the BookSerializer.
    Tests serialization and deserialization of Book model.
    """
    
    def setUp(self):
        """
        Set up test data for BookSerializer tests.
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
        self.serializer = BookSerializer(instance=self.book)
    
    def test_contains_expected_fields(self):
        """
        Test that serializer contains all expected fields.
        """
        data = self.serializer.data
        expected_fields = (
            'id', 'title', 'author', 'genre', 'isbn', 'publication_date',
            'cover_image_url', 'quantity', 'created_at', 'updated_at'
        )
        
        self.assertEqual(set(data.keys()), set(expected_fields))
    
    def test_field_content(self):
        """
        Test that serialized data matches model data.
        """
        data = self.serializer.data
        
        self.assertEqual(data['title'], self.book_data['title'])
        self.assertEqual(data['author'], self.book_data['author'])
        self.assertEqual(data['genre'], self.book_data['genre'])
        self.assertEqual(data['isbn'], self.book_data['isbn'])
        self.assertEqual(data['publication_date'], str(self.book_data['publication_date']))
        self.assertEqual(data['cover_image_url'], self.book_data['cover_image_url'])
        self.assertEqual(data['quantity'], self.book_data['quantity'])
    
    def test_create_book(self):
        """
        Test creating a book using serializer.
        """
        new_book_data = {
            'title': 'New Book',
            'author': 'New Author',
            'genre': 'New Genre',
            'isbn': '9876543210987',
            'publication_date': '2023-01-01',
            'cover_image_url': 'http://example.com/new-cover.jpg',
            'quantity': 10
        }
        
        serializer = BookSerializer(data=new_book_data)
        self.assertTrue(serializer.is_valid())
        
        book = serializer.save()
        self.assertEqual(book.title, new_book_data['title'])
        self.assertEqual(book.author, new_book_data['author'])
        self.assertEqual(book.genre, new_book_data['genre'])
        self.assertEqual(book.isbn, new_book_data['isbn'])
        self.assertEqual(str(book.publication_date), new_book_data['publication_date'])
        self.assertEqual(book.cover_image_url, new_book_data['cover_image_url'])
        self.assertEqual(book.quantity, new_book_data['quantity'])
    
    def test_update_book(self):
        """
        Test updating a book using serializer.
        """
        update_data = {
            'title': 'Updated Book',
            'quantity': 15
        }
        
        serializer = BookSerializer(instance=self.book, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        book = serializer.save()
        self.assertEqual(book.title, update_data['title'])
        self.assertEqual(book.quantity, update_data['quantity'])
        # Other fields should remain unchanged
        self.assertEqual(book.author, self.book_data['author'])


class UserBriefSerializerTest(TestCase):
    """
    Test case for the UserBriefSerializer.
    Tests serialization of User model for nested representations.
    """
    
    def setUp(self):
        """
        Set up test data for UserBriefSerializer tests.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        self.serializer = UserBriefSerializer(instance=self.user)
    
    def test_contains_expected_fields(self):
        """
        Test that serializer contains all expected fields.
        """
        data = self.serializer.data
        expected_fields = ('id', 'username', 'email')
        
        self.assertEqual(set(data.keys()), set(expected_fields))
    
    def test_field_content(self):
        """
        Test that serialized data matches model data.
        """
        data = self.serializer.data
        
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)


class BookBriefSerializerTest(TestCase):
    """
    Test case for the BookBriefSerializer.
    Tests serialization of Book model for nested representations.
    """
    
    def setUp(self):
        """
        Set up test data for BookBriefSerializer tests.
        """
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Test Genre',
            quantity=5
        )
        
        self.serializer = BookBriefSerializer(instance=self.book)
    
    def test_contains_expected_fields(self):
        """
        Test that serializer contains all expected fields.
        """
        data = self.serializer.data
        expected_fields = ('id', 'title', 'author')
        
        self.assertEqual(set(data.keys()), set(expected_fields))
    
    def test_field_content(self):
        """
        Test that serialized data matches model data.
        """
        data = self.serializer.data
        
        self.assertEqual(data['title'], self.book.title)
        self.assertEqual(data['author'], self.book.author)


class BorrowRecordSerializerTest(TestCase):
    """
    Test case for the BorrowRecordSerializer.
    Tests serialization and deserialization of BorrowRecord model.
    """
    
    def setUp(self):
        """
        Set up test data for BorrowRecordSerializer tests.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Test Genre',
            quantity=5
        )
        
        self.borrow_record = BorrowRecord.objects.create(
            user=self.user,
            book=self.book,
            status='PENDING'
        )
        
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.user
        
        self.serializer = BorrowRecordSerializer(
            instance=self.borrow_record,
            context={'request': self.request}
        )
    
    def test_contains_expected_fields(self):
        """
        Test that serializer contains all expected fields.
        """
        data = self.serializer.data
        expected_fields = (
            'id', 'user', 'book', 'book_id', 'borrow_date', 'due_date',
            'return_date', 'status', 'created_at', 'updated_at'
        )
        
        self.assertEqual(set(data.keys()), set(expected_fields))
    
    def test_field_content(self):
        """
        Test that serialized data matches model data.
        """
        data = self.serializer.data
        
        self.assertEqual(data['user']['id'], self.user.id)
        self.assertEqual(data['user']['username'], self.user.username)
        self.assertEqual(data['book']['id'], self.book.id)
        self.assertEqual(data['book']['title'], self.book.title)
        self.assertEqual(data['status'], self.borrow_record.status)
    
    def test_create_borrow_record(self):
        """
        Test creating a borrow record using serializer.
        """
        new_book = Book.objects.create(
            title='New Book',
            author='New Author',
            genre='New Genre',
            quantity=3
        )
        
        data = {
            'book_id': new_book.id
        }
        
        serializer = BorrowRecordSerializer(
            data=data,
            context={'request': self.request}
        )
        
        self.assertTrue(serializer.is_valid())
        
        # The serializer doesn't actually create the borrow record,
        # it's handled by the BorrowingService in the view
        # So we just check that validation passes


class AdminBorrowRecordSerializerTest(TestCase):
    """
    Test case for the AdminBorrowRecordSerializer.
    Tests serialization of BorrowRecord model for admin views.
    """
    
    def setUp(self):
        """
        Set up test data for AdminBorrowRecordSerializer tests.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Test Genre',
            quantity=5
        )
        
        self.borrow_record = BorrowRecord.objects.create(
            user=self.user,
            book=self.book,
            status='APPROVED',
            borrow_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14)
        )
        
        self.serializer = AdminBorrowRecordSerializer(instance=self.borrow_record)
    
    def test_contains_expected_fields(self):
        """
        Test that serializer contains all expected fields.
        """
        data = self.serializer.data
        expected_fields = (
            'id', 'user', 'book', 'borrow_date', 'due_date',
            'return_date', 'status', 'created_at', 'updated_at'
        )
        
        self.assertEqual(set(data.keys()), set(expected_fields))
    
    def test_field_content(self):
        """
        Test that serialized data matches model data.
        """
        data = self.serializer.data
        
        self.assertEqual(data['user']['id'], self.user.id)
        self.assertEqual(data['user']['username'], self.user.username)
        self.assertEqual(data['book']['id'], self.book.id)
        self.assertEqual(data['book']['title'], self.book.title)
        self.assertEqual(data['status'], self.borrow_record.status)
        self.assertEqual(data['borrow_date'], str(self.borrow_record.borrow_date))
        self.assertEqual(data['due_date'], str(self.borrow_record.due_date))


class ReservationSerializerTest(TestCase):
    """
    Test case for the ReservationSerializer.
    Tests serialization and deserialization of Reservation model.
    """
    
    def setUp(self):
        """
        Set up test data for ReservationSerializer tests.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Test Genre',
            quantity=0  # Book is unavailable
        )
        
        self.reservation = Reservation.objects.create(
            user=self.user,
            book=self.book,
            status='PENDING',
            reservation_date=timezone.now().date()
        )
        
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.user
        
        self.serializer = ReservationSerializer(
            instance=self.reservation,
            context={'request': self.request}
        )
    
    def test_contains_expected_fields(self):
        """
        Test that serializer contains all expected fields.
        """
        data = self.serializer.data
        expected_fields = (
            'id', 'user', 'book', 'book_id', 'status', 'reservation_date',
            'notification_sent', 'created_at', 'updated_at'
        )
        
        self.assertEqual(set(data.keys()), set(expected_fields))
    
    def test_field_content(self):
        """
        Test that serialized data matches model data.
        """
        data = self.serializer.data
        
        self.assertEqual(data['user']['id'], self.user.id)
        self.assertEqual(data['user']['username'], self.user.username)
        self.assertEqual(data['book']['id'], self.book.id)
        self.assertEqual(data['book']['title'], self.book.title)
        self.assertEqual(data['status'], self.reservation.status)
        self.assertEqual(data['reservation_date'], str(self.reservation.reservation_date))
        self.assertEqual(data['notification_sent'], self.reservation.notification_sent)
    
    def test_create_reservation(self):
        """
        Test creating a reservation using serializer.
        """
        new_book = Book.objects.create(
            title='New Book',
            author='New Author',
            genre='New Genre',
            quantity=0  # Book is unavailable
        )
        
        data = {
            'book_id': new_book.id
        }
        
        serializer = ReservationSerializer(
            data=data,
            context={'request': self.request}
        )
        
        self.assertTrue(serializer.is_valid())
        
        # The serializer doesn't actually create the reservation,
        # it's handled by the ReservationService in the view
        # So we just check that validation passes


class FineSerializerTest(TestCase):
    """
    Test case for the FineSerializer.
    Tests serialization of Fine model.
    """
    
    def setUp(self):
        """
        Set up test data for FineSerializer tests.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Test Genre',
            quantity=5
        )
        
        self.borrow_record = BorrowRecord.objects.create(
            user=self.user,
            book=self.book,
            status='RETURNED',
            borrow_date=timezone.now().date() - timedelta(days=20),
            due_date=timezone.now().date() - timedelta(days=6),
            return_date=timezone.now().date()
        )
        
        self.fine = Fine.objects.create(
            borrow_record=self.borrow_record,
            user=self.user,
            amount=Decimal('3.00'),
            reason='Overdue return',
            status='PENDING',
            days_overdue=6
        )
        
        self.serializer = FineSerializer(instance=self.fine)
    
    def test_contains_expected_fields(self):
        """
        Test that serializer contains all expected fields.
        """
        data = self.serializer.data
        expected_fields = (
            'id', 'borrow_record', 'amount', 'reason', 'status',
            'days_overdue', 'created_at', 'updated_at'
        )
        
        self.assertEqual(set(data.keys()), set(expected_fields))
    
    def test_field_content(self):
        """
        Test that serialized data matches model data.
        """
        data = self.serializer.data
        
        self.assertEqual(data['borrow_record'], self.borrow_record.id)
        self.assertEqual(data['amount'], '3.00')  # Decimal is serialized as string
        self.assertEqual(data['reason'], self.fine.reason)
        self.assertEqual(data['status'], self.fine.status)
        self.assertEqual(data['days_overdue'], self.fine.days_overdue)


class AdminFineSerializerTest(TestCase):
    """
    Test case for the AdminFineSerializer.
    Tests serialization of Fine model for admin views.
    """
    
    def setUp(self):
        """
        Set up test data for AdminFineSerializer tests.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Test Genre',
            quantity=5
        )
        
        self.borrow_record = BorrowRecord.objects.create(
            user=self.user,
            book=self.book,
            status='RETURNED',
            borrow_date=timezone.now().date() - timedelta(days=20),
            due_date=timezone.now().date() - timedelta(days=6),
            return_date=timezone.now().date()
        )
        
        self.fine = Fine.objects.create(
            borrow_record=self.borrow_record,
            user=self.user,
            amount=Decimal('3.00'),
            reason='Overdue return',
            status='PENDING',
            days_overdue=6
        )
        
        self.serializer = AdminFineSerializer(instance=self.fine)
    
    def test_contains_expected_fields(self):
        """
        Test that serializer contains all expected fields.
        """
        data = self.serializer.data
        expected_fields = (
            'id', 'borrow_record', 'user', 'amount', 'reason', 'status',
            'days_overdue', 'created_at', 'updated_at'
        )
        
        self.assertEqual(set(data.keys()), set(expected_fields))
    
    def test_field_content(self):
        """
        Test that serialized data matches model data.
        """
        data = self.serializer.data
        
        self.assertEqual(data['user']['id'], self.user.id)
        self.assertEqual(data['user']['username'], self.user.username)
        self.assertEqual(data['amount'], '3.00')  # Decimal is serialized as string
        self.assertEqual(data['reason'], self.fine.reason)
        self.assertEqual(data['status'], self.fine.status)
        self.assertEqual(data['days_overdue'], self.fine.days_overdue)
