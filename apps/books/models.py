import uuid
from django.conf import settings
from django.db import models


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100, blank=True)
    isbn = models.CharField(max_length=32, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    cover_image_url = models.URLField(blank=True)
    available_copies = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"


class BorrowRecord(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "PENDING"
        APPROVED = "APPROVED", "APPROVED"
        REJECTED = "REJECTED", "REJECTED"
        RETURN_PENDING = "RETURN_PENDING", "RETURN_PENDING"
        RETURNED = "RETURNED", "RETURNED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user} - {self.book} ({self.status})"


class Fine(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "PENDING"
        PAID = "PAID", "PAID"
        WAIVED = "WAIVED", "WAIVED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    borrow_record = models.ForeignKey(BorrowRecord, on_delete=models.CASCADE, related_name="fines")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=64, default="OVERDUE")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Fine {self.id} - {self.amount} ({self.status})"
