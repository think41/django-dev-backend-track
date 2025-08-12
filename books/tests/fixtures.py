"""
Test fixtures for books app.

This module provides reusable fixtures for setting up test data
for books, borrow records, reservations, and fines.
"""

import pytest
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model

from books.models import Book, BorrowRecord, Reservation, Fine

User = get_user_model()


class UserFixture:
    """
    Fixture for creating test users with different roles.
    """
    
    @staticmethod
    def create_admin_user():
        """Create an admin user for testing."""
        return User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            is_active=True,
            role='admin'
        )
    
    @staticmethod
    def create_librarian_user():
        """Create a librarian user for testing."""
        return User.objects.create_user(
            username='librarian',
            email='librarian@example.com',
            password='LibrarianPass123!',
            is_active=True,
            role='librarian'
        )
    
    @staticmethod
    def create_member_user():
        """Create an active member user for testing."""
        return User.objects.create_user(
            username='member',
            email='member@example.com',
            password='MemberPass123!',
            is_active=True,
            role='member'
        )
    
    @staticmethod
    def create_inactive_user():
        """Create an inactive member user for testing."""
        return User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='InactivePass123!',
            is_active=False,
            role='member'
        )


class BookFixture:
    """
    Fixture for creating test books.
    """
    
    @staticmethod
    def create_book(title='Test Book', author='Test Author', genre='Fiction', 
                   isbn='1234567890123', quantity=5):
        """Create a book with the given parameters."""
        return Book.objects.create(
            title=title,
            author=author,
            genre=genre,
            isbn=isbn,
            publication_date=timezone.now().date(),
            cover_image_url='http://example.com/cover.jpg',
            quantity=quantity
        )
    
    @staticmethod
    def create_available_book():
        """Create a book with available copies."""
        return BookFixture.create_book(
            title='Available Book',
            author='Test Author',
            genre='Fiction',
            isbn='1111111111111',
            quantity=5
        )
    
    @staticmethod
    def create_unavailable_book():
        """Create a book with no available copies."""
        return BookFixture.create_book(
            title='Unavailable Book',
            author='Test Author',
            genre='Non-Fiction',
            isbn='2222222222222',
            quantity=0
        )


class BorrowFixture:
    """
    Fixture for creating test borrow records.
    """
    
    @staticmethod
    def create_pending_borrow(user, book):
        """Create a pending borrow record."""
        return BorrowRecord.objects.create(
            user=user,
            book=book,
            status='PENDING'
        )
    
    @staticmethod
    def create_approved_borrow(user, book, days_ago=0, due_in_days=14):
        """Create an approved borrow record."""
        borrow_date = timezone.now().date() - timedelta(days=days_ago)
        due_date = borrow_date + timedelta(days=due_in_days)
        
        return BorrowRecord.objects.create(
            user=user,
            book=book,
            status='APPROVED',
            borrow_date=borrow_date,
            due_date=due_date
        )
    
    @staticmethod
    def create_returned_borrow(user, book, days_ago=20, due_days_ago=6):
        """Create a returned borrow record."""
        borrow_date = timezone.now().date() - timedelta(days=days_ago)
        due_date = timezone.now().date() - timedelta(days=due_days_ago)
        return_date = timezone.now().date()
        
        return BorrowRecord.objects.create(
            user=user,
            book=book,
            status='RETURNED',
            borrow_date=borrow_date,
            due_date=due_date,
            return_date=return_date
        )
    
    @staticmethod
    def create_rejected_borrow(user, book):
        """Create a rejected borrow record."""
        return BorrowRecord.objects.create(
            user=user,
            book=book,
            status='REJECTED'
        )


class ReservationFixture:
    """
    Fixture for creating test reservations.
    """
    
    @staticmethod
    def create_pending_reservation(user, book):
        """Create a pending reservation."""
        return Reservation.objects.create(
            user=user,
            book=book,
            status='PENDING',
            reservation_date=timezone.now().date()
        )
    
    @staticmethod
    def create_fulfilled_reservation(user, book):
        """Create a fulfilled reservation."""
        return Reservation.objects.create(
            user=user,
            book=book,
            status='FULFILLED',
            reservation_date=timezone.now().date() - timedelta(days=5),
            notification_sent=True
        )
    
    @staticmethod
    def create_cancelled_reservation(user, book):
        """Create a cancelled reservation."""
        return Reservation.objects.create(
            user=user,
            book=book,
            status='CANCELLED',
            reservation_date=timezone.now().date() - timedelta(days=3)
        )


class FineFixture:
    """
    Fixture for creating test fines.
    """
    
    @staticmethod
    def create_pending_fine(borrow_record, user, amount=Decimal('3.00'), days_overdue=6):
        """Create a pending fine."""
        return Fine.objects.create(
            borrow_record=borrow_record,
            user=user,
            amount=amount,
            reason='Overdue return',
            status='PENDING',
            days_overdue=days_overdue
        )
    
    @staticmethod
    def create_paid_fine(borrow_record, user, amount=Decimal('3.00'), days_overdue=6):
        """Create a paid fine."""
        return Fine.objects.create(
            borrow_record=borrow_record,
            user=user,
            amount=amount,
            reason='Overdue return',
            status='PAID',
            days_overdue=days_overdue
        )
