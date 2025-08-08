from decimal import Decimal
from django.db import transaction

from ..models import BorrowRecord, Fine


class FineService:
    OVERDUE_DAYS = 14
    DAILY_RATE = Decimal("2.00")

    @staticmethod
    @transaction.atomic
    def calculate_and_create_fine_if_overdue(record: BorrowRecord) -> Fine | None:
        """Create a fine if the record is overdue when returned.
        Policy: more than OVERDUE_DAYS between borrow_date and return_date.
        Amount = days_over * DAILY_RATE.
        """
        if not record.borrow_date or not record.return_date:
            return None
        days = (record.return_date - record.borrow_date).days
        if days <= FineService.OVERDUE_DAYS:
            return None
        days_over = days - FineService.OVERDUE_DAYS
        amount = FineService.DAILY_RATE * days_over
        return Fine.objects.create(borrow_record=record, amount=amount, reason="OVERDUE")

    @staticmethod
    @transaction.atomic
    def pay_fine(fine: Fine) -> Fine:
        if fine.status != Fine.Status.PENDING:
            raise ValueError("Only PENDING fines can be paid")
        fine.status = Fine.Status.PAID
        fine.save(update_fields=["status", "updated_at"])
        return fine

    @staticmethod
    @transaction.atomic
    def waive_fine(fine: Fine) -> Fine:
        if fine.status != Fine.Status.PENDING:
            raise ValueError("Only PENDING fines can be waived")
        fine.status = Fine.Status.WAIVED
        fine.save(update_fields=["status", "updated_at"])
        return fine
