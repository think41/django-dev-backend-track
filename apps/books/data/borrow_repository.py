from typing import Optional
from ..models import BorrowRecord


class BorrowRepository:
    @staticmethod
    def create(**kwargs) -> BorrowRecord:
        return BorrowRecord.objects.create(**kwargs)

    @staticmethod
    def get_by_id(record_id) -> Optional[BorrowRecord]:
        try:
            return BorrowRecord.objects.get(id=record_id)
        except BorrowRecord.DoesNotExist:
            return None

    @staticmethod
    def list_pending():
        return BorrowRecord.objects.filter(status=BorrowRecord.Status.PENDING).order_by("-created_at")

    @staticmethod
    def list_for_user(user_id):
        return BorrowRecord.objects.filter(user_id=user_id).order_by("-created_at")
