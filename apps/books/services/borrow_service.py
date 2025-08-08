from datetime import date
from django.db import transaction

from ..models import Book, BorrowRecord
from ..data import BorrowRepository


class BorrowService:
    @staticmethod
    @transaction.atomic
    def request_borrow(user, book: Book) -> BorrowRecord:
        existing_pending = BorrowRecord.objects.filter(user=user, book=book, status=BorrowRecord.Status.PENDING).exists()
        if existing_pending:
            raise ValueError("Outstanding pending request exists.")
        record = BorrowRepository.create(user=user, book=book, status=BorrowRecord.Status.PENDING)
        return record

    @staticmethod
    @transaction.atomic
    def approve_request(record: BorrowRecord) -> BorrowRecord:
        if record.status != BorrowRecord.Status.PENDING:
            raise ValueError("Only PENDING requests can be approved.")
        if record.book.available_copies <= 0:
            raise ValueError("No available copies.")
        record.status = BorrowRecord.Status.APPROVED
        record.borrow_date = date.today()
        record.save(update_fields=["status", "borrow_date", "updated_at"])
        record.book.available_copies -= 1
        record.book.save(update_fields=["available_copies", "updated_at"])
        return record

    @staticmethod
    @transaction.atomic
    def reject_request(record: BorrowRecord) -> BorrowRecord:
        if record.status != BorrowRecord.Status.PENDING:
            raise ValueError("Only PENDING requests can be rejected.")
        record.status = BorrowRecord.Status.REJECTED
        record.save(update_fields=["status", "updated_at"])
        return record

    @staticmethod
    @transaction.atomic
    def return_book(record: BorrowRecord) -> BorrowRecord:
        if record.status != BorrowRecord.Status.APPROVED:
            raise ValueError("Only APPROVED records can be returned.")
        record.status = BorrowRecord.Status.RETURNED
        record.return_date = date.today()
        record.save(update_fields=["status", "return_date", "updated_at"])
        record.book.available_copies += 1
        record.book.save(update_fields=["available_copies", "updated_at"])
        return record
