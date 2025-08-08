from django.db import transaction
from django.utils import timezone

from .models import Book, BorrowRecord


class BorrowingService:
    @staticmethod
    @transaction.atomic
    def request_borrow(user, book: Book) -> BorrowRecord:
        existing = BorrowRecord.objects.filter(user=user, book=book, status__in=[
            BorrowRecord.Status.PENDING,
            BorrowRecord.Status.APPROVED,
        ]).exists()
        if existing:
            raise ValueError("You already have an active request for this book")
        if book.quantity <= 0:
            raise ValueError("Book is not available")
        return BorrowRecord.objects.create(user=user, book=book)

    @staticmethod
    @transaction.atomic
    def approve_request(record: BorrowRecord) -> BorrowRecord:
        if record.status != BorrowRecord.Status.PENDING:
            raise ValueError("Only pending requests can be approved")
        if record.book.quantity <= 0:
            raise ValueError("Book is not available")
        record.status = BorrowRecord.Status.APPROVED
        record.borrow_date = timezone.now()
        record.save(update_fields=["status", "borrow_date", "updated_at"])
        record.book.quantity -= 1
        record.book.save(update_fields=["quantity", "updated_at"])
        return record

    @staticmethod
    @transaction.atomic
    def reject_request(record: BorrowRecord) -> BorrowRecord:
        if record.status != BorrowRecord.Status.PENDING:
            raise ValueError("Only pending requests can be rejected")
        record.status = BorrowRecord.Status.REJECTED
        record.save(update_fields=["status", "updated_at"])
        return record

    @staticmethod
    @transaction.atomic
    def return_book(record: BorrowRecord) -> BorrowRecord:
        if record.status != BorrowRecord.Status.APPROVED:
            raise ValueError("Only approved borrows can be returned")
        record.status = BorrowRecord.Status.RETURNED
        record.return_date = timezone.now()
        record.save(update_fields=["status", "return_date", "updated_at"])
        record.book.quantity += 1
        record.book.save(update_fields=["quantity", "updated_at"])
        return record

