from django.db.models import Q
from rest_framework import generics, permissions, response, status

from users.permissions import IsAdmin

from .models import Book, BorrowRecord
from .serializers import BookSerializer, BorrowRecordSerializer
from .services import BorrowingService


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(author__icontains=search) | Q(genre__icontains=search)
            )
        return queryset


class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]


class BorrowRequestView(generics.CreateAPIView):
    serializer_class = BorrowRecordSerializer

    def create(self, request, *args, **kwargs):
        book_id = request.data.get("book_id")
        try:
            book = Book.objects.get(id=book_id)
            record = BorrowingService.request_borrow(request.user, book)
        except Book.DoesNotExist:
            return response.Response({"detail": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return response.Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(record)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)


class ReturnBookView(generics.GenericAPIView):
    serializer_class = BorrowRecordSerializer

    def post(self, request, *args, **kwargs):
        record_id = request.data.get("borrow_record_id")
        try:
            record = BorrowRecord.objects.get(id=record_id, user=request.user)
            record = BorrowingService.return_book(record)
        except BorrowRecord.DoesNotExist:
            return response.Response({"detail": "Borrow record not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return response.Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(record)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class AdminBorrowListView(generics.ListAPIView):
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = BorrowRecord.objects.select_related("user", "book").order_by("-request_date")
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset


class AdminApproveBorrowView(generics.UpdateAPIView):
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAdmin]
    queryset = BorrowRecord.objects.select_related("user", "book")

    def patch(self, request, *args, **kwargs):
        record = self.get_object()
        try:
            record = BorrowingService.approve_request(record)
        except ValueError as e:
            return response.Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return response.Response(self.get_serializer(record).data)


class AdminRejectBorrowView(generics.UpdateAPIView):
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAdmin]
    queryset = BorrowRecord.objects.select_related("user", "book")

    def patch(self, request, *args, **kwargs):
        record = self.get_object()
        try:
            record = BorrowingService.reject_request(record)
        except ValueError as e:
            return response.Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return response.Response(self.get_serializer(record).data)

