from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Book, BorrowRecord, Fine
from ..services import BorrowService, FineService
from .serializers import BookSerializer, BorrowRecordSerializer, FineSerializer


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

    # Support simple search and filtering without relying on global filter backends
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        q = request.query_params.get("q")
        title = request.query_params.get("title")
        author = request.query_params.get("author")
        genre = request.query_params.get("genre")
        ordering = request.query_params.get("ordering")

        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(author__icontains=q) | qs.filter(genre__icontains=q)
        if title:
            qs = qs.filter(title__icontains=title)
        if author:
            qs = qs.filter(author__icontains=author)
        if genre:
            qs = qs.filter(genre__iexact=genre)
        if ordering in ("title", "-title", "author", "-author", "created_at", "-created_at"):
            qs = qs.order_by(ordering)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class BorrowViewSet(viewsets.GenericViewSet):
    queryset = BorrowRecord.objects.all().order_by("-created_at")
    serializer_class = BorrowRecordSerializer

    def get_permissions(self):
        if self.action in ["approvals", "approve", "reject", "return_approve", "records"]:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=["post"], url_path="borrow")
    def borrow(self, request):
        book_id = request.data.get("book_id")
        if not book_id:
            return Response({"detail": "'book_id' is required"}, status=status.HTTP_400_BAD_REQUEST)
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
        if not record_id:
            return Response({"detail": "'borrow_record_id' is required"}, status=status.HTTP_400_BAD_REQUEST)
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

    @action(detail=False, methods=["get"], url_path="records")
    def records(self, request):
        """Admin: List all borrow records with optional status filter.
        Query param: status in [PENDING, APPROVED, REJECTED, RETURN_PENDING, RETURNED]
        """
        status_param = request.query_params.get("status")
        qs = BorrowRecord.objects.all().order_by("-created_at")
        if status_param:
            valid_statuses = {s for s, _ in BorrowRecord.Status.choices}
            if status_param not in valid_statuses:
                return Response({"detail": f"Invalid status. Valid: {sorted(valid_statuses)}"}, status=status.HTTP_400_BAD_REQUEST)
            qs = qs.filter(status=status_param)
        return Response(BorrowRecordSerializer(qs, many=True).data)

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


class FineViewSet(viewsets.GenericViewSet):
    queryset = Fine.objects.all().order_by("-created_at")
    serializer_class = FineSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "waive"]:
            return [IsAdmin()]
        if self.action in ["pay"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def list(self, request, *args, **kwargs):  # type: ignore[override]
        status_param = request.query_params.get("status")
        qs = Fine.objects.all().order_by("-created_at")
        if status_param:
            valid_statuses = {s for s, _ in Fine.Status.choices}
            if status_param not in valid_statuses:
                return Response({"detail": f"Invalid status. Valid: {sorted(valid_statuses)}"}, status=status.HTTP_400_BAD_REQUEST)
            qs = qs.filter(status=status_param)
        return Response(FineSerializer(qs, many=True).data)

    def retrieve(self, request, pk=None, *args, **kwargs):  # type: ignore[override]
        try:
            fine = Fine.objects.get(id=pk)
        except Fine.DoesNotExist:
            return Response({"detail": "Fine not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(FineSerializer(fine).data)

    @action(detail=True, methods=["post"], url_path="pay")
    def pay(self, request, pk=None):
        try:
            fine = Fine.objects.get(id=pk)
        except Fine.DoesNotExist:
            return Response({"detail": "Fine not found"}, status=status.HTTP_404_NOT_FOUND)
        # Allow admin or the owner of the borrow record
        if not (getattr(request.user, "role", "") == "ADMIN" or fine.borrow_record.user_id == request.user.id):
            return Response({"detail": "Not permitted"}, status=status.HTTP_403_FORBIDDEN)
        try:
            FineService.pay_fine(fine)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Fine marked as PAID"})

    @action(detail=True, methods=["post"], url_path="waive")
    def waive(self, request, pk=None):
        try:
            fine = Fine.objects.get(id=pk)
        except Fine.DoesNotExist:
            return Response({"detail": "Fine not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            FineService.waive_fine(fine)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Fine waived"})