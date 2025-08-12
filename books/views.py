from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Book, BorrowRecord, Reservation, Fine
from .serializers import (
    BookSerializer,
    BorrowRecordSerializer,
    AdminBorrowRecordSerializer,
    ReservationSerializer,
    FineSerializer,
    AdminFineSerializer
)
from .services import BorrowingService, ReservationService, FineService
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
    search_fields = ['title', 'author', 'genre', 'isbn']
    ordering_fields = ['title', 'author', 'genre', 'publication_date', 'created_at']
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
            
            borrow_record, fine = BorrowingService.return_book(borrow_record)
            
            response_data = {"message": "Book returned successfully."}
            if fine:
                response_data["fine"] = {
                    "id": fine.id,
                    "amount": fine.amount,
                    "reason": fine.reason,
                    "days_overdue": fine.days_overdue
                }
                
            return Response(response_data, status=status.HTTP_200_OK)
            
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


class ReservationCreateView(generics.CreateAPIView):
    """
    API endpoint for members to reserve a book that is currently unavailable.
    """
    serializer_class = ReservationSerializer
    permission_classes = [IsActiveUser]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            book = serializer.validated_data['book']
            reservation = ReservationService.reserve_book(request.user, book)
            
            return Response(
                {"message": "Book reservation created successfully."},
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReservationCancelView(APIView):
    """
    API endpoint for members to cancel their book reservation.
    """
    permission_classes = [IsActiveUser]
    
    def post(self, request):
        reservation_id = request.data.get('reservation_id')
        
        if not reservation_id:
            return Response(
                {"error": "reservation_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the reservation and verify it belongs to the user
            reservation = get_object_or_404(Reservation, id=reservation_id)
            
            if reservation.user != request.user:
                return Response(
                    {"error": "This reservation does not belong to you."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            ReservationService.cancel_reservation(reservation)
            return Response({"message": "Reservation cancelled successfully."}, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserReservationListView(generics.ListAPIView):
    """
    API endpoint for members to list their reservations.
    """
    serializer_class = ReservationSerializer
    permission_classes = [IsActiveUser]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['reservation_date', 'created_at']
    ordering = ['-reservation_date']
    
    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)


class AdminReservationListView(generics.ListAPIView):
    """
    API endpoint for admins to list all reservations.
    """
    serializer_class = ReservationSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['reservation_date', 'created_at']
    ordering = ['-reservation_date']
    
    def get_queryset(self):
        return Reservation.objects.all()


class UserFineListView(generics.ListAPIView):
    """
    API endpoint for members to list their fines.
    """
    serializer_class = FineSerializer
    permission_classes = [IsActiveUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Fine.objects.filter(user=self.request.user)


class AdminFineListView(generics.ListAPIView):
    """
    API endpoint for admins to list all fines.
    """
    serializer_class = AdminFineSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Fine.objects.all()


class AdminFinePaymentView(APIView):
    """
    API endpoint for admins to mark a fine as paid.
    """
    permission_classes = [IsAdmin]
    
    def patch(self, request, id):
        try:
            fine = get_object_or_404(Fine, id=id)
            FineService.mark_as_paid(fine)
            return Response({"message": "Fine marked as paid."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminFineWaiverView(APIView):
    """
    API endpoint for admins to waive a fine.
    """
    permission_classes = [IsAdmin]
    
    def patch(self, request, id):
        try:
            fine = get_object_or_404(Fine, id=id)
            FineService.waive_fine(fine)
            return Response({"message": "Fine waived successfully."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
