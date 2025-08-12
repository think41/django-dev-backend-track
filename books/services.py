from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from decimal import Decimal
from .models import Book, BorrowRecord, Reservation, Fine


class BorrowingService:
    """
    Service for managing the state transitions of a BorrowRecord and its side effects.
    """
    
    @staticmethod
    @transaction.atomic
    def request_borrow(user, book):
        """
        Creates a new borrow request for a book.
        
        Args:
            user: The user requesting to borrow the book
            book: The book to be borrowed
            
        Returns:
            BorrowRecord: The newly created borrow record with PENDING status
            
        Raises:
            ValueError: If the book quantity is 0 or if the user already has a pending or approved request for this book
        """
        # Check if book is available
        if book.quantity <= 0:
            raise ValueError("This book is currently not available for borrowing.")
        
        # Check if user already has a pending or approved request for this book
        existing_request = BorrowRecord.objects.filter(
            user=user,
            book=book,
            status__in=['PENDING', 'APPROVED']
        ).exists()
        
        if existing_request:
            raise ValueError("You already have a pending or approved request for this book.")
        
        # Create new borrow record with PENDING status
        borrow_record = BorrowRecord.objects.create(
            user=user,
            book=book,
            status='PENDING'
        )
        
        return borrow_record
    
    @staticmethod
    @transaction.atomic
    def approve_request(borrow_record):
        """
        Approves a borrow request.
        
        Args:
            borrow_record: The borrow record to approve
            
        Returns:
            BorrowRecord: The updated borrow record with APPROVED status
            
        Raises:
            ValueError: If the record is not in PENDING state or if the book quantity is 0
        """
        # Check if record is in PENDING state
        if borrow_record.status != 'PENDING':
            raise ValueError("Only pending requests can be approved.")
        
        # Check if book is still available
        book = borrow_record.book
        if book.quantity <= 0:
            raise ValueError("This book is no longer available for borrowing.")
        
        # Update book quantity
        book.quantity -= 1
        book.save(update_fields=['quantity'])
        
        # Set borrow date and due date (14 days from now)
        today = timezone.now().date()
        due_date = today + timedelta(days=14)
        
        # Update borrow record
        borrow_record.status = 'APPROVED'
        borrow_record.borrow_date = today
        borrow_record.due_date = due_date
        borrow_record.save(update_fields=['status', 'borrow_date', 'due_date'])
        
        return borrow_record
    
    @staticmethod
    @transaction.atomic
    def reject_request(borrow_record):
        """
        Rejects a borrow request.
        
        Args:
            borrow_record: The borrow record to reject
            
        Returns:
            BorrowRecord: The updated borrow record with REJECTED status
            
        Raises:
            ValueError: If the record is not in PENDING state
        """
        # Check if record is in PENDING state
        if borrow_record.status != 'PENDING':
            raise ValueError("Only pending requests can be rejected.")
        
        # Update borrow record
        borrow_record.status = 'REJECTED'
        borrow_record.save(update_fields=['status'])
        
        return borrow_record
    
    @staticmethod
    @transaction.atomic
    def return_book(borrow_record):
        """
        Processes a book return.
        
        Args:
            borrow_record: The borrow record to mark as returned
            
        Returns:
            tuple: (BorrowRecord, Fine or None) - The updated borrow record with RETURNED status and a Fine object if the book was returned late
            
        Raises:
            ValueError: If the record is not in APPROVED state
        """
        # Check if record is in APPROVED state
        if borrow_record.status != 'APPROVED':
            raise ValueError("Only approved borrows can be returned.")
        
        # Update book quantity
        book = borrow_record.book
        book.quantity += 1
        book.save(update_fields=['quantity'])
        
        # Set return date
        return_date = timezone.now().date()
        
        # Update borrow record
        borrow_record.status = 'RETURNED'
        borrow_record.return_date = return_date
        borrow_record.save(update_fields=['status', 'return_date'])
        
        # Check if book is returned late and create fine if needed
        fine = None
        if borrow_record.due_date and return_date > borrow_record.due_date:
            days_overdue = (return_date - borrow_record.due_date).days
            fine = FineService.create_fine(
                borrow_record=borrow_record,
                days_overdue=days_overdue,
                reason="Overdue return"
            )
        
        # Check for pending reservations for this book
        ReservationService.check_for_available_reservations(book)
        
        return borrow_record, fine


class ReservationService:
    """
    Service for managing book reservations and their fulfillment.
    """
    
    @staticmethod
    @transaction.atomic
    def reserve_book(user, book):
        """
        Creates a new reservation for a book.
        
        Args:
            user: The user requesting to reserve the book
            book: The book to be reserved
            
        Returns:
            Reservation: The newly created reservation with PENDING status
            
        Raises:
            ValueError: If the book is available (should borrow instead) or if the user already has a pending reservation for this book
        """
        # Check if book is unavailable (quantity = 0)
        if book.quantity > 0:
            raise ValueError("This book is currently available. Please borrow it instead of reserving.")
        
        # Check if user already has a pending reservation for this book
        existing_reservation = Reservation.objects.filter(
            user=user,
            book=book,
            status='PENDING'
        ).exists()
        
        if existing_reservation:
            raise ValueError("You already have a pending reservation for this book.")
        
        # Create new reservation with PENDING status
        reservation = Reservation.objects.create(
            user=user,
            book=book,
            status='PENDING'
        )
        
        return reservation
    
    @staticmethod
    @transaction.atomic
    def fulfill_reservation(reservation):
        """
        Marks a reservation as fulfilled when the book becomes available.
        
        Args:
            reservation: The reservation to fulfill
            
        Returns:
            Reservation: The updated reservation with FULFILLED status
            
        Raises:
            ValueError: If the reservation is not in PENDING state
        """
        # Check if reservation is in PENDING state
        if reservation.status != 'PENDING':
            raise ValueError("Only pending reservations can be fulfilled.")
        
        # Update reservation
        reservation.status = 'FULFILLED'
        reservation.notification_sent = True
        reservation.save(update_fields=['status', 'notification_sent'])
        
        return reservation
    
    @staticmethod
    @transaction.atomic
    def cancel_reservation(reservation):
        """
        Cancels a reservation.
        
        Args:
            reservation: The reservation to cancel
            
        Returns:
            Reservation: The updated reservation with CANCELLED status
            
        Raises:
            ValueError: If the reservation is not in PENDING state
        """
        # Check if reservation is in PENDING state
        if reservation.status != 'PENDING':
            raise ValueError("Only pending reservations can be cancelled.")
        
        # Update reservation
        reservation.status = 'CANCELLED'
        reservation.save(update_fields=['status'])
        
        return reservation
    
    @staticmethod
    @transaction.atomic
    def check_for_available_reservations(book):
        """
        When a book is returned, checks if there are any pending reservations for it and fulfills the oldest one.
        
        Args:
            book: The book that has been returned
            
        Returns:
            Reservation or None: The fulfilled reservation, if any
        """
        if book.quantity > 0:
            # Get the oldest pending reservation for this book
            oldest_reservation = Reservation.objects.filter(
                book=book,
                status='PENDING'
            ).order_by('reservation_date').first()
            
            if oldest_reservation:
                return ReservationService.fulfill_reservation(oldest_reservation)
        
        return None


class FineService:
    """
    Service for managing fines for overdue books.
    """
    
    # Fine amount per day overdue (in dollars)
    FINE_RATE_PER_DAY = Decimal('0.50')
    
    @staticmethod
    def calculate_fine(days_overdue):
        """
        Calculates the fine amount based on the number of days overdue.
        
        Args:
            days_overdue: The number of days the book was overdue
            
        Returns:
            Decimal: The calculated fine amount
        """
        return FineService.FINE_RATE_PER_DAY * Decimal(days_overdue)
    
    @staticmethod
    @transaction.atomic
    def create_fine(borrow_record, days_overdue, reason="Overdue return"):
        """
        Creates a new fine record associated with a borrow record.
        
        Args:
            borrow_record: The borrow record associated with this fine
            days_overdue: The number of days the book was overdue
            reason: The reason for the fine
            
        Returns:
            Fine: The newly created fine with PENDING status
        """
        amount = FineService.calculate_fine(days_overdue)
        
        fine = Fine.objects.create(
            borrow_record=borrow_record,
            user=borrow_record.user,
            amount=amount,
            reason=reason,
            days_overdue=days_overdue,
            status='PENDING'
        )
        
        return fine
    
    @staticmethod
    @transaction.atomic
    def mark_as_paid(fine):
        """
        Marks a fine as paid.
        
        Args:
            fine: The fine to mark as paid
            
        Returns:
            Fine: The updated fine with PAID status
            
        Raises:
            ValueError: If the fine is not in PENDING state
        """
        # Check if fine is in PENDING state
        if fine.status != 'PENDING':
            raise ValueError("Only pending fines can be marked as paid.")
        
        # Update fine
        fine.status = 'PAID'
        fine.save(update_fields=['status'])
        
        return fine
    
    @staticmethod
    @transaction.atomic
    def waive_fine(fine):
        """
        Waives a fine.
        
        Args:
            fine: The fine to waive
            
        Returns:
            Fine: The updated fine with WAIVED status
            
        Raises:
            ValueError: If the fine is not in PENDING state
        """
        # Check if fine is in PENDING state
        if fine.status != 'PENDING':
            raise ValueError("Only pending fines can be waived.")
        
        # Update fine
        fine.status = 'WAIVED'
        fine.save(update_fields=['status'])
        
        return fine
