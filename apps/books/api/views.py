from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Book, BorrowRecord
from ..services import BookService, BorrowService
from .serializers import BookSerializer, BorrowRecordSerializer


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", "") == "ADMIN")


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("title")
    serializer_class = BookSerializer
    filterset_fields = ["genre"]
    search_fields = ["title", "author", "genre", "isbn"]
    ordering_fields = ["title", "author", "created_at"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]


class BorrowViewSet(viewsets.GenericViewSet):
    queryset = BorrowRecord.objects.all().order_by("-created_at")
    serializer_class = BorrowRecordSerializer

    def get_permissions(self):
        if self.action in ["approvals", "approve", "reject", "return_approve"]:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=["post"], url_path="borrow")
    def borrow(self, request):
        book_id = request.data.get("book_id")
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"detail": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            record = BorrowService.request_borrow(request.user, book)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Borrow request submitted", "id": str(record.id)}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="return")
    def return_book(self, request):
        record_id = request.data.get("borrow_record_id")
        try:
            record = BorrowRecord.objects.get(id=record_id, user=request.user)
        except BorrowRecord.DoesNotExist:
            return Response({"detail": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            record = BorrowService.return_book(record)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Book returned"})

    @action(detail=False, methods=["get"], url_path="approvals")
    def approvals(self, request):
        records = BorrowRecord.objects.filter(status=BorrowRecord.Status.PENDING).order_by("-created_at")
        return Response(BorrowRecordSerializer(records, many=True).data)

    @action(detail=True, methods=["patch"], url_path="approve")
    def approve(self, request, pk=None):
        try:
            record = BorrowRecord.objects.get(id=pk)
        except BorrowRecord.DoesNotExist:
            return Response({"detail": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            BorrowService.approve_request(record)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Borrow request approved"})

    @action(detail=True, methods=["patch"], url_path="reject")
    def reject(self, request, pk=None):
        try:
            record = BorrowRecord.objects.get(id=pk)
        except BorrowRecord.DoesNotExist:
            return Response({"detail": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            BorrowService.reject_request(record)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Borrow request rejected"})

    @action(detail=True, methods=["patch"], url_path="return/approve")
    def return_approve(self, request, pk=None):
        try:
            record = BorrowRecord.objects.get(id=pk)
        except BorrowRecord.DoesNotExist:
            return Response({"detail": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            BorrowService.return_book(record)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Return processed"})

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        records = BorrowRecord.objects.filter(user=request.user).order_by("-created_at")
        return Response(BorrowRecordSerializer(records, many=True).data)
