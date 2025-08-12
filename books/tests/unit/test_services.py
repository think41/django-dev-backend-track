import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from books.models import Book, BorrowRecord, Reservation, Fine
from books.services import BorrowingService, ReservationService, FineService

User = get_user_model()


class BorrowingServiceTest(TestCase):
    """
    Test case for the BorrowingService.
    Tests all service methods and business logic.
    """
    
    def setUp(self):
        """
        Set up test data for BorrowingService tests.
        """
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        # Create test books
        self.available_book = Book.objects.create(
            title='Available Book',
            author='Test Author',
            genre='Test Genre',
            quantity=5
        )
        
        self.unavailable_book = Book.objects.create(
            title='Unavailable Book',
            author='Test Author',
            genre='Test Genre',
            quantity=0
        )
        
        # Create a test borrow record
        self.pending_borrow = BorrowRecord.objects.create(
            user=self.user,
            book=self.available_book,
            status='PENDING'
        )
        
        self.approved_borrow = BorrowRecord.objects.create(
            user=self.user,
            book=self.available_book,
            status='APPROVED',
            borrow_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14)
        )
    
    def test_request_borrow_success(self):
        """
        Test successful borrow request creation.
        """
        new_book = Book.objects.create(
            title='New Book',
            author='New Author',
            genre='New Genre',
            quantity=3
        )
        
        borrow_record = BorrowingService.request_borrow(self.user, new_book)
        
        self.assertEqual(borrow_record.user, self.user)
        self.assertEqual(borrow_record.book, new_book)
        self.assertEqual(borrow_record.status, 'PENDING')
        self.assertIsNone(borrow_record.borrow_date)
        self.assertIsNone(borrow_record.due_date)
        self.assertIsNone(borrow_record.return_date)
    
    def test_request_borrow_unavailable_book(self):
        """
        Test borrow request for unavailable book raises ValueError.
        """
        with self.assertRaises(ValueError):
            BorrowingService.request_borrow(self.user, self.unavailable_book)
    
    def test_request_borrow_existing_request(self):
        """
        Test borrow request for book with existing request raises ValueError.
        """
        with self.assertRaises(ValueError):
            BorrowingService.request_borrow(self.user, self.available_book)
    
    def test_approve_request_success(self):
        """
        Test successful approval of borrow request.
        """
        initial_quantity = self.available_book.quantity
        
        borrow_record = BorrowingService.approve_request(self.pending_borrow)
        
        # Refresh book from database
        self.available_book.refresh_from_db()
        
        self.assertEqual(borrow_record.status, 'APPROVED')
        self.assertIsNotNone(borrow_record.borrow_date)
        self.assertIsNotNone(borrow_record.due_date)
        self.assertEqual(self.available_book.quantity, initial_quantity - 1)
    
    def test_approve_request_non_pending(self):
        """
        Test approval of non-pending request raises ValueError.
        """
        non_pending = BorrowRecord.objects.create(
            user=self.user,
            book=self.available_book,
            status='REJECTED'
        )
        
        with self.assertRaises(ValueError):
            BorrowingService.approve_request(non_pending)
    
    def test_approve_request_unavailable_book(self):
        """
        Test approval of request for unavailable book raises ValueError.
        """
        pending_unavailable = BorrowRecord.objects.create(
            user=self.user,
            book=self.unavailable_book,
            status='PENDING'
        )
        
        with self.assertRaises(ValueError):
            BorrowingService.approve_request(pending_unavailable)
    
    def test_reject_request_success(self):
        """
        Test successful rejection of borrow request.
        """
        borrow_record = BorrowingService.reject_request(self.pending_borrow)
        
        self.assertEqual(borrow_record.status, 'REJECTED')
    
    def test_reject_request_non_pending(self):
        """
        Test rejection of non-pending request raises ValueError.
        """
        with self.assertRaises(ValueError):
            BorrowingService.reject_request(self.approved_borrow)
    
    def test_return_book_success(self):
        """
        Test successful return of borrowed book.
        """
        initial_quantity = self.available_book.quantity
        today = timezone.now().date()
        
        # Return on time
        borrow_record, fine = BorrowingService.return_book(self.approved_borrow)
        
        # Refresh book from database
        self.available_book.refresh_from_db()
        
        self.assertEqual(borrow_record.status, 'RETURNED')
        self.assertIsNotNone(borrow_record.return_date)
        self.assertEqual(self.available_book.quantity, initial_quantity + 1)
        self.assertIsNone(fine)  # No fine for on-time return
    
    def test_return_book_overdue(self):
        """
        Test return of overdue book creates fine.
        """
        # Create an overdue borrow record
        past_date = timezone.now().date() - timedelta(days=20)
        due_date = timezone.now().date() - timedelta(days=6)  # 6 days overdue
        
        overdue_borrow = BorrowRecord.objects.create(
            user=self.user,
            book=self.available_book,
            status='APPROVED',
            borrow_date=past_date,
            due_date=due_date
        )
        
        borrow_record, fine = BorrowingService.return_book(overdue_borrow)
        
        self.assertEqual(borrow_record.status, 'RETURNED')
        self.assertIsNotNone(fine)
        self.assertEqual(fine.days_overdue, 6)
        self.assertEqual(fine.amount, Decimal('3.00'))  # $0.50 per day
    
    def test_return_book_not_approved(self):
        """
        Test return of non-approved book raises ValueError.
        """
        with self.assertRaises(ValueError):
            BorrowingService.return_book(self.pending_borrow)
    
    @patch('books.services.ReservationService.check_for_available_reservations')
    def test_return_book_with_reservation(self, mock_check_reservations):
        """
        Test return of book checks for reservations.
        """
        # Mock the reservation check
        mock_reservation = MagicMock()
        mock_check_reservations.return_value = mock_reservation
        
        BorrowingService.return_book(self.approved_borrow)
        
        # Verify reservation check was called
        mock_check_reservations.assert_called_once_with(self.available_book)


class ReservationServiceTest(TestCase):
    """
    Test case for the ReservationService.
    Tests all service methods and business logic.
    """
    
    def setUp(self):
        """
        Set up test data for ReservationService tests.
        """
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        self.another_user = User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        # Create test books
        self.available_book = Book.objects.create(
            title='Available Book',
            author='Test Author',
            genre='Test Genre',
            quantity=5
        )
        
        self.unavailable_book = Book.objects.create(
            title='Unavailable Book',
            author='Test Author',
            genre='Test Genre',
            quantity=0
        )
        
        # Create a test reservation
        self.pending_reservation = Reservation.objects.create(
            user=self.user,
            book=self.unavailable_book,
            status='PENDING',
            reservation_date=timezone.now().date()
        )
    
    def test_reserve_book_success(self):
        """
        Test successful book reservation.
        """
        # Create another unavailable book
        another_unavailable = Book.objects.create(
            title='Another Unavailable',
            author='Another Author',
            genre='Another Genre',
            quantity=0
        )
        
        reservation = ReservationService.reserve_book(self.another_user, another_unavailable)
        
        self.assertEqual(reservation.user, self.another_user)
        self.assertEqual(reservation.book, another_unavailable)
        self.assertEqual(reservation.status, 'PENDING')
        self.assertIsNotNone(reservation.reservation_date)
        self.assertFalse(reservation.notification_sent)
    
    def test_reserve_available_book(self):
        """
        Test reservation of available book raises ValueError.
        """
        with self.assertRaises(ValueError):
            ReservationService.reserve_book(self.user, self.available_book)
    
    def test_reserve_book_existing_reservation(self):
        """
        Test reservation of book with existing reservation raises ValueError.
        """
        with self.assertRaises(ValueError):
            ReservationService.reserve_book(self.user, self.unavailable_book)
    
    def test_fulfill_reservation_success(self):
        """
        Test successful fulfillment of reservation.
        """
        reservation = ReservationService.fulfill_reservation(self.pending_reservation)
        
        self.assertEqual(reservation.status, 'FULFILLED')
        self.assertTrue(reservation.notification_sent)
    
    def test_fulfill_reservation_non_pending(self):
        """
        Test fulfillment of non-pending reservation raises ValueError.
        """
        non_pending = Reservation.objects.create(
            user=self.user,
            book=self.unavailable_book,
            status='CANCELLED',
            reservation_date=timezone.now().date()
        )
        
        with self.assertRaises(ValueError):
            ReservationService.fulfill_reservation(non_pending)
    
    def test_cancel_reservation_success(self):
        """
        Test successful cancellation of reservation.
        """
        reservation = ReservationService.cancel_reservation(self.pending_reservation)
        
        self.assertEqual(reservation.status, 'CANCELLED')
    
    def test_cancel_reservation_non_pending(self):
        """
        Test cancellation of non-pending reservation raises ValueError.
        """
        non_pending = Reservation.objects.create(
            user=self.user,
            book=self.unavailable_book,
            status='FULFILLED',
            reservation_date=timezone.now().date(),
            notification_sent=True
        )
        
        with self.assertRaises(ValueError):
            ReservationService.cancel_reservation(non_pending)
    
    def test_check_for_available_reservations_success(self):
        """
        Test successful check for available reservations.
        """
        # Make the book available
        self.unavailable_book.quantity = 1
        self.unavailable_book.save()
        
        # Check for reservations
        fulfilled_reservation = ReservationService.check_for_available_reservations(self.unavailable_book)
        
        # Refresh reservation from database
        self.pending_reservation.refresh_from_db()
        
        self.assertEqual(fulfilled_reservation, self.pending_reservation)
        self.assertEqual(self.pending_reservation.status, 'FULFILLED')
        self.assertTrue(self.pending_reservation.notification_sent)
    
    def test_check_for_available_reservations_no_reservations(self):
        """
        Test check for available reservations with no pending reservations.
        """
        # Make the book available
        self.unavailable_book.quantity = 1
        self.unavailable_book.save()
        
        # Cancel the reservation
        self.pending_reservation.status = 'CANCELLED'
        self.pending_reservation.save()
        
        # Check for reservations
        result = ReservationService.check_for_available_reservations(self.unavailable_book)
        
        self.assertIsNone(result)
    
    def test_check_for_available_reservations_multiple_reservations(self):
        """
        Test check for available reservations with multiple pending reservations.
        """
        # Make the book available
        self.unavailable_book.quantity = 1
        self.unavailable_book.save()
        
        # Create an older reservation
        older_date = timezone.now().date() - timedelta(days=5)
        older_reservation = Reservation.objects.create(
            user=self.another_user,
            book=self.unavailable_book,
            status='PENDING',
            reservation_date=older_date
        )
        
        # Check for reservations - should fulfill the older one first
        fulfilled_reservation = ReservationService.check_for_available_reservations(self.unavailable_book)
        
        # Refresh reservations from database
        older_reservation.refresh_from_db()
        self.pending_reservation.refresh_from_db()
        
        self.assertEqual(fulfilled_reservation, older_reservation)
        self.assertEqual(older_reservation.status, 'FULFILLED')
        self.assertTrue(older_reservation.notification_sent)
        self.assertEqual(self.pending_reservation.status, 'PENDING')
        self.assertFalse(self.pending_reservation.notification_sent)


class FineServiceTest(TestCase):
    """
    Test case for the FineService.
    Tests all service methods and business logic.
    """
    
    def setUp(self):
        """
        Set up test data for FineService tests.
        """
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True,
            role='member'
        )
        
        # Create test books
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
    
    def test_calculate_fine(self):
        """
        Test fine calculation based on days overdue.
        """
        # Test with 5 days overdue
        amount = FineService.calculate_fine(5)
        self.assertEqual(amount, Decimal('2.50'))  # $0.50 per day
        
        # Test with 0 days overdue
        amount = FineService.calculate_fine(0)
        self.assertEqual(amount, Decimal('0.00'))
        
        # Test with negative days (shouldn't happen, but should handle gracefully)
        amount = FineService.calculate_fine(-1)
        self.assertEqual(amount, Decimal('0.00'))
    
    def test_create_fine(self):
        """
        Test fine creation.
        """
        # Create a new borrow record for testing
        new_borrow = BorrowRecord.objects.create(
            user=self.user,
            book=self.book,
            status='RETURNED',
            borrow_date=timezone.now().date() - timedelta(days=17),
            due_date=timezone.now().date() - timedelta(days=3),
            return_date=timezone.now().date()
        )
        
        fine = FineService.create_fine(new_borrow, 3, "Test reason")
        
        self.assertEqual(fine.borrow_record, new_borrow)
        self.assertEqual(fine.user, self.user)
        self.assertEqual(fine.amount, Decimal('1.50'))  # $0.50 * 3 days
        self.assertEqual(fine.reason, "Test reason")
        self.assertEqual(fine.status, 'PENDING')
        self.assertEqual(fine.days_overdue, 3)
    
    def test_mark_as_paid(self):
        """
        Test marking fine as paid.
        """
        fine = FineService.mark_as_paid(self.fine)
        
        self.assertEqual(fine.status, 'PAID')
    
    def test_mark_as_paid_non_pending(self):
        """
        Test marking non-pending fine as paid raises ValueError.
        """
        non_pending = Fine.objects.create(
            borrow_record=self.borrow_record,
            user=self.user,
            amount=Decimal('2.50'),
            reason='Overdue return',
            status='WAIVED',
            days_overdue=5
        )
        
        with self.assertRaises(ValueError):
            FineService.mark_as_paid(non_pending)
    
    def test_waive_fine(self):
        """
        Test waiving fine.
        """
        fine = FineService.waive_fine(self.fine)
        
        self.assertEqual(fine.status, 'WAIVED')
    
    def test_waive_fine_non_pending(self):
        """
        Test waiving non-pending fine raises ValueError.
        """
        non_pending = Fine.objects.create(
            borrow_record=self.borrow_record,
            user=self.user,
            amount=Decimal('2.50'),
            reason='Overdue return',
            status='PAID',
            days_overdue=5
        )
        
        with self.assertRaises(ValueError):
            FineService.waive_fine(non_pending)
