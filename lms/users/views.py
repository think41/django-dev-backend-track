"""
Views for the Users app.

This module contains all API views for user management, profile operations,
and borrowing functionality as specified in the users spec.md file.
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime, timedelta
from dateutil import parser

from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    AdminUserListSerializer,
    BorrowRequestSerializer,
    BorrowHistorySerializer,
    BorrowRecordSerializer,
    BorrowApprovalSerializer
)
from .permissions import IsAdmin, IsActiveMember, IsOwnerOrAdmin, IsActiveUser
from lms.books.models import Book

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Creates new users with PENDING status.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


# Admin User Management Views
class AdminUserListView(generics.ListAPIView):
    """
    API endpoint for admins to view all users.
    GET /api/users/admin/
    """
    queryset = User.objects.all()
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdmin]


@api_view(['PATCH'])
@permission_classes([IsAdmin])
def approve_member_registration(request, user_id):
    """
    API endpoint for admins to approve member registrations.
    PATCH /api/users/admin/approve/{user_id}/
    """
    user = get_object_or_404(User, id=user_id)
    
    if user.status != 'PENDING':
        return Response(
            {'error': 'User is not in pending status'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.status = 'ACTIVE'
    user.save()
    
    serializer = AdminUserListSerializer(user)
    return Response({
        'message': 'User registration approved successfully',
        'user': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_borrow_records(request):
    """
    API endpoint for admins to view all borrow records.
    GET /api/users/admin/borrow-records/
    """
    # Get query parameters for filtering
    status_filter = request.GET.get('status')
    user_id_filter = request.GET.get('user_id')
    
    # Get all users with borrowing records
    users_with_borrows = User.objects.exclude(borrowed_books=[])
    
    if user_id_filter:
        users_with_borrows = users_with_borrows.filter(id=user_id_filter)
    
    borrow_records = []
    
    for user in users_with_borrows:
        for record in user.borrowed_books:
            # Apply status filter if provided
            if status_filter and record.get('status') != status_filter:
                continue
            
            # Get book information
            try:
                book = Book.objects.get(id=record['book_id'])
                book_title = book.title
            except Book.DoesNotExist:
                book_title = f"Unknown Book (ID: {record['book_id']})"
            
            # Parse dates
            request_date = parser.parse(record['request_date'])
            approval_date = parser.parse(record['approval_date']) if record.get('approval_date') else None
            return_date = parser.parse(record['return_date']) if record.get('return_date') else None
            due_date = parser.parse(record['due_date']) if record.get('due_date') else None
            
            borrow_records.append({
                'user_id': user.id,
                'username': user.username,
                'book_id': record['book_id'],
                'book_title': book_title,
                'request_date': request_date,
                'approval_date': approval_date,
                'return_date': return_date,
                'due_date': due_date,
                'status': record['status']
            })
    
    # Sort by request date (most recent first)
    borrow_records.sort(key=lambda x: x['request_date'], reverse=True)
    
    serializer = BorrowRecordSerializer(borrow_records, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAdmin])
def approve_borrow_request(request, user_id, book_id):
    """
    API endpoint for admins to approve borrow requests.
    PATCH /api/users/admin/approve-borrow/{user_id}/{book_id}/
    """
    user = get_object_or_404(User, id=user_id)
    book = get_object_or_404(Book, id=book_id)
    
    # Check if book is available
    if book.available_copies <= 0:
        return Response(
            {'error': 'Book is not available for borrowing'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Find the pending borrow request
    pending_request = None
    for record in user.borrowed_books:
        if (record['book_id'] == int(book_id) and 
            record['status'] == 'PENDING'):
            pending_request = record
            break
    
    if not pending_request:
        return Response(
            {'error': 'No pending borrow request found for this book'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Parse optional due date from request
    serializer = BorrowApprovalSerializer(data=request.data)
    if serializer.is_valid():
        due_date = serializer.validated_data.get('due_date')
        if not due_date:
            # Default to 14 days from now
            due_date = datetime.now() + timedelta(days=14)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Update the borrow request
    user.update_borrow_status(
        book_id=int(book_id),
        status='APPROVED',
        approval_date=datetime.now(),
        due_date=due_date
    )
    
    # Decrease available copies
    book.available_copies -= 1
    book.save()
    
    return Response({
        'message': 'Borrow request approved successfully',
        'due_date': due_date.isoformat()
    })


@api_view(['PATCH'])
@permission_classes([IsAdmin])
def reject_borrow_request(request, user_id, book_id):
    """
    API endpoint for admins to reject borrow requests.
    PATCH /api/users/admin/reject-borrow/{user_id}/{book_id}/
    """
    user = get_object_or_404(User, id=user_id)
    
    # Find the pending borrow request
    pending_request = None
    for record in user.borrowed_books:
        if (record['book_id'] == int(book_id) and 
            record['status'] == 'PENDING'):
            pending_request = record
            break
    
    if not pending_request:
        return Response(
            {'error': 'No pending borrow request found for this book'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Update the borrow request status
    user.update_borrow_status(
        book_id=int(book_id),
        status='REJECTED'
    )
    
    return Response({
        'message': 'Borrow request rejected successfully'
    })


# User Profile Views
class UserProfileView(generics.RetrieveAPIView):
    """
    API endpoint for users to view their own profile.
    GET /api/users/profile/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """
    API endpoint for users to update their profile.
    PUT/PATCH /api/users/profile/
    """
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


# Member Borrowing Views
@api_view(['POST'])
@permission_classes([IsActiveMember])
def request_borrow_book(request):
    """
    API endpoint for members to request borrowing a book.
    POST /api/users/borrow/request/
    """
    serializer = BorrowRequestSerializer(data=request.data)
    if serializer.is_valid():
        book_id = serializer.validated_data['book_id']
        book = get_object_or_404(Book, id=book_id)
        
        # Check if user already has a pending/active request for this book
        for record in request.user.borrowed_books:
            if (record['book_id'] == book_id and 
                record['status'] in ['PENDING', 'APPROVED']):
                return Response(
                    {'error': 'You already have a pending or active request for this book'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Add borrow request
        borrow_record = request.user.add_borrow_request(book_id)
        
        return Response({
            'message': 'Borrow request submitted successfully',
            'borrow_record': borrow_record
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsActiveMember])
def return_book(request, book_id):
    """
    API endpoint for members to return a borrowed book.
    PATCH /api/users/borrow/return/{book_id}/
    """
    book = get_object_or_404(Book, id=book_id)
    
    # Find the approved, not-returned borrow record
    active_record = None
    for record in request.user.borrowed_books:
        if (record['book_id'] == int(book_id) and 
            record['status'] == 'APPROVED' and
            not record.get('return_date')):
            active_record = record
            break
    
    if not active_record:
        return Response(
            {'error': 'No active borrowing record found for this book'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Return the book
    request.user.return_book(int(book_id))
    
    # Increase available copies
    book.available_copies += 1
    book.save()
    
    return Response({
        'message': 'Book returned successfully'
    })


@api_view(['GET'])
@permission_classes([IsActiveMember])
def borrowing_history(request):
    """
    API endpoint for members to view their borrowing history.
    GET /api/users/borrow/history/
    """
    history_data = []
    
    for record in request.user.borrowed_books:
        # Get book information
        try:
            book = Book.objects.get(id=record['book_id'])
            book_title = book.title
        except Book.DoesNotExist:
            book_title = f"Unknown Book (ID: {record['book_id']})"
        
        # Parse dates
        request_date = parser.parse(record['request_date'])
        approval_date = parser.parse(record['approval_date']) if record.get('approval_date') else None
        return_date = parser.parse(record['return_date']) if record.get('return_date') else None
        due_date = parser.parse(record['due_date']) if record.get('due_date') else None
        
        history_data.append({
            'book_id': record['book_id'],
            'book_title': book_title,
            'request_date': request_date,
            'approval_date': approval_date,
            'return_date': return_date,
            'due_date': due_date,
            'status': record['status']
        })
    
    # Sort by request date (most recent first)
    history_data.sort(key=lambda x: x['request_date'], reverse=True)
    
    serializer = BorrowHistorySerializer(history_data, many=True)
    return Response(serializer.data)