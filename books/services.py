from django.utils import timezone
from django.db import transaction
from .models import Book, BorrowRecord


class BorrowingService:
    @staticmethod
    def request_borrow(user, book):
        """
        Checks if the book is available and creates a new BorrowRecord with PENDING status.
        """
        # Check if book is available
        if book.quantity <= 0:
            raise ValueError("Book is not available")
        
        # Check if user already has a pending request for this book
        existing_request = BorrowRecord.objects.filter(
            user=user,
            book=book,
            status__in=['PENDING', 'APPROVED']
        ).exists()
        
        if existing_request:
            raise ValueError("You already have an outstanding request for this book")
        
        # Create new borrow record
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
        Sets the record's status to APPROVED, sets the borrow_date, 
        and decrements the associated book's quantity.
        """
        if borrow_record.status != 'PENDING':
            raise ValueError("Only pending requests can be approved")
        
        if borrow_record.book.quantity <= 0:
            raise ValueError("Book is not available")
        
        # Update borrow record
        borrow_record.status = 'APPROVED'
        borrow_record.borrow_date = timezone.now().date()
        borrow_record.save()
        
        # Decrement book quantity
        borrow_record.book.quantity -= 1
        borrow_record.book.save()
        
        return borrow_record
    
    @staticmethod
    def reject_request(borrow_record):
        """
        Sets the record's status to REJECTED.
        """
        if borrow_record.status != 'PENDING':
            raise ValueError("Only pending requests can be rejected")
        
        borrow_record.status = 'REJECTED'
        borrow_record.save()
        return borrow_record
    
    @staticmethod
    @transaction.atomic
    def return_book(borrow_record):
        """
        Sets the record's status to RETURNED, sets the return_date, 
        and increments the associated book's quantity.
        """
        if borrow_record.status != 'APPROVED':
            raise ValueError("Only approved records can be returned")
        
        # Update borrow record
        borrow_record.status = 'RETURNED'
        borrow_record.return_date = timezone.now().date()
        borrow_record.save()
        
        # Increment book quantity
        borrow_record.book.quantity += 1
        borrow_record.book.save()
        
        return borrow_record 