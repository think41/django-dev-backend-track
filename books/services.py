from django.utils import timezone
from django.db import transaction
from .models import Book, BorrowRecord


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
        
        # Update borrow record
        borrow_record.status = 'APPROVED'
        borrow_record.borrow_date = timezone.now().date()
        borrow_record.save(update_fields=['status', 'borrow_date'])
        
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
            BorrowRecord: The updated borrow record with RETURNED status
            
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
        
        # Update borrow record
        borrow_record.status = 'RETURNED'
        borrow_record.return_date = timezone.now().date()
        borrow_record.save(update_fields=['status', 'return_date'])
        
        return borrow_record
