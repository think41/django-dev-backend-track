from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Book, BorrowRecord
from .serializers import (
    BookSerializer,
    BorrowRecordSerializer,
    AdminBorrowRecordSerializer
)
from .services import BorrowingService
from .permissions import IsAdmin, IsActiveUser, IsAdminOrReadOnly





class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing books.
    Allows authenticated users to view books.
    Only admin users can create, update, or delete books.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsActiveUser, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'genre']
    ordering_fields = ['title', 'author', 'genre', 'created_at']
    ordering = ['title']


class BorrowRequestView(generics.CreateAPIView):
    """
    API endpoint for members to request to borrow a book.
    """
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsActiveUser]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            book = serializer.validated_data['book']
            borrow_record = BorrowingService.request_borrow(request.user, book)
            
            return Response(
                {"message": "Borrow request submitted successfully. Waiting for admin approval."},
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BookReturnView(APIView):
    """
    API endpoint for members to return a borrowed book.
    """
    permission_classes = [IsActiveUser]
    
    def post(self, request):
        borrow_record_id = request.data.get('borrow_record_id')
        
        if not borrow_record_id:
            return Response(
                {"error": "borrow_record_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the borrow record and verify it belongs to the user
            borrow_record = get_object_or_404(BorrowRecord, id=borrow_record_id)
            
            if borrow_record.user != request.user:
                return Response(
                    {"error": "This borrow record does not belong to you."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            BorrowingService.return_book(borrow_record)
            return Response({"message": "Book returned successfully."}, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminBorrowListView(generics.ListAPIView):
    """
    API endpoint for admins to list all borrow records.
    """
    serializer_class = AdminBorrowRecordSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'updated_at', 'borrow_date', 'return_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return BorrowRecord.objects.all()


class AdminBorrowApprovalView(APIView):
    """
    API endpoint for admins to approve a borrow request.
    """
    permission_classes = [IsAdmin]
    
    def patch(self, request, id):
        try:
            borrow_record = get_object_or_404(BorrowRecord, id=id)
            BorrowingService.approve_request(borrow_record)
            return Response({"message": "Borrow request approved."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminBorrowRejectionView(APIView):
    """
    API endpoint for admins to reject a borrow request.
    """
    permission_classes = [IsAdmin]
    
    def patch(self, request, id):
        try:
            borrow_record = get_object_or_404(BorrowRecord, id=id)
            BorrowingService.reject_request(borrow_record)
            return Response({"message": "Borrow request rejected."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
