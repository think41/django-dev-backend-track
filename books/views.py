from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Book, BorrowRecord
from .serializers import (
    BookSerializer, BookCreateSerializer, BorrowRequestSerializer, 
    ReturnBookSerializer, BorrowRecordSerializer, BooksMessageResponseSerializer
)
from .services import BorrowingService


# Book Catalog Operations
@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description='Search by title, author, or genre', type=openapi.TYPE_STRING),
    ],
    responses={
        200: BookSerializer(many=True),
        401: 'Unauthorized - Authentication required'
    },
    operation_description='Retrieve a list of all books in the catalog with optional search functionality.',
    tags=['Books - Catalog']
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_books(request):
    """
    GET /api/books/
    Retrieves a list of all books in the catalog. Supports searching.
    """
    books = Book.objects.all()
    
    # Handle search parameter
    search = request.query_params.get('search')
    if search:
        books = books.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(genre__icontains=search)
        )
    
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=BookCreateSerializer,
    responses={
        201: BookSerializer,
        400: 'Bad Request - Invalid data',
        403: 'Forbidden - Admin access required'
    },
    operation_description='Create a new book entry in the catalog. Admin only.',
    tags=['Books - Catalog']
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_book(request):
    """
    POST /api/books/
    Creates a new book entry in the catalog. Admin only.
    """
    # Check if user is admin
    if request.user.role != 'admin':
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = BookCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        book = serializer.save()
        response_serializer = BookSerializer(book)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={
        200: BookSerializer,
        404: 'Not Found - Book does not exist'
    },
    operation_description='Retrieve a single book by its ID.',
    tags=['Books - Catalog']
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_book(request, book_id):
    """
    GET /api/books/{id}/
    Retrieves a single book by its ID.
    """
    try:
        book = Book.objects.get(id=book_id)
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Book.DoesNotExist:
        return Response(
            {"detail": "Book not found."},
            status=status.HTTP_404_NOT_FOUND
        )


@swagger_auto_schema(
    method='put',
    request_body=BookCreateSerializer,
    responses={
        200: BookSerializer,
        400: 'Bad Request - Invalid data',
        403: 'Forbidden - Admin access required',
        404: 'Not Found - Book does not exist'
    },
    operation_description='Update all fields of a specific book. Admin only.',
    tags=['Books - Catalog']
)
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_book(request, book_id):
    """
    PUT /api/books/{id}/
    Updates all fields of a specific book. Admin only.
    """
    # Check if user is admin
    if request.user.role != 'admin':
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response(
            {"detail": "Book not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = BookCreateSerializer(book, data=request.data)
    
    if serializer.is_valid():
        book = serializer.save()
        response_serializer = BookSerializer(book)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    responses={
        204: 'No Content - Book deleted successfully',
        403: 'Forbidden - Admin access required',
        404: 'Not Found - Book does not exist'
    },
    operation_description='Delete a book from the catalog. Admin only.',
    tags=['Books - Catalog']
)
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_book(request, book_id):
    """
    DELETE /api/books/{id}/
    Deletes a book from the catalog. Admin only.
    """
    # Check if user is admin
    if request.user.role != 'admin':
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        book = Book.objects.get(id=book_id)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Book.DoesNotExist:
        return Response(
            {"detail": "Book not found."},
            status=status.HTTP_404_NOT_FOUND
        )


# Book Borrowing Operations
@swagger_auto_schema(
    method='post',
    request_body=BorrowRequestSerializer,
    responses={
        201: BooksMessageResponseSerializer,
        400: 'Bad Request - Book unavailable or duplicate request'
    },
    operation_description='Submit a request to borrow a book. Members only.',
    tags=['Books - Borrowing']
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def borrow_book(request):
    """
    POST /api/books/borrow/
    Allows a member to submit a request to borrow a book.
    """
    serializer = BorrowRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        book_id = serializer.validated_data['book_id']
        
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response(
                {"detail": "Book not found."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            BorrowingService.request_borrow(request.user, book)
            return Response(
                {"message": "Borrow request submitted successfully. Waiting for admin approval."},
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=ReturnBookSerializer,
    responses={
        200: BooksMessageResponseSerializer,
        400: 'Bad Request - Invalid record or not owned by user'
    },
    operation_description='Return a borrowed book. Members only.',
    tags=['Books - Borrowing']
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def return_book(request):
    """
    POST /api/books/return/
    Allows a member to return a book they have borrowed.
    """
    serializer = ReturnBookSerializer(data=request.data)
    
    if serializer.is_valid():
        record_id = serializer.validated_data['borrow_record_id']
        
        try:
            borrow_record = BorrowRecord.objects.get(id=record_id, user=request.user)
        except BorrowRecord.DoesNotExist:
            return Response(
                {"detail": "Borrow record not found or does not belong to you."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            BorrowingService.return_book(borrow_record)
            return Response(
                {"message": "Book returned successfully."},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin Borrow Management
@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, description='Filter by status (PENDING/APPROVED/REJECTED/RETURNED)', type=openapi.TYPE_STRING),
    ],
    responses={
        200: BorrowRecordSerializer(many=True),
        403: 'Forbidden - Admin access required'
    },
    operation_description='Retrieve a list of all borrow records with optional status filtering. Admin only.',
    tags=['Books - Admin Borrowing']
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_borrow_records(request):
    """
    GET /api/books/admin/borrow/
    Retrieves a list of all borrow records. Admin only.
    """
    # Check if user is admin
    if request.user.role != 'admin':
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    records = BorrowRecord.objects.all().select_related('user', 'book')
    
    # Handle status filter
    status_filter = request.query_params.get('status')
    if status_filter and status_filter.upper() in ['PENDING', 'APPROVED', 'REJECTED', 'RETURNED']:
        records = records.filter(status=status_filter.upper())
    
    serializer = BorrowRecordSerializer(records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='patch',
    responses={
        200: BooksMessageResponseSerializer,
        400: 'Bad Request - Invalid request state or book unavailable',
        403: 'Forbidden - Admin access required',
        404: 'Not Found - Borrow record does not exist'
    },
    operation_description='Approve a pending borrow request. Admin only.',
    tags=['Books - Admin Borrowing']
)
@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def approve_borrow_request(request, record_id):
    """
    PATCH /api/books/admin/borrow/{id}/approve/
    Approves a pending borrow request. Admin only.
    """
    # Check if user is admin
    if request.user.role != 'admin':
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        borrow_record = BorrowRecord.objects.get(id=record_id)
    except BorrowRecord.DoesNotExist:
        return Response(
            {"detail": "Borrow record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        BorrowingService.approve_request(borrow_record)
        return Response(
            {"message": "Borrow request approved."},
            status=status.HTTP_200_OK
        )
    except ValueError as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@swagger_auto_schema(
    method='patch',
    responses={
        200: BooksMessageResponseSerializer,
        400: 'Bad Request - Invalid request state',
        403: 'Forbidden - Admin access required',
        404: 'Not Found - Borrow record does not exist'
    },
    operation_description='Reject a pending borrow request. Admin only.',
    tags=['Books - Admin Borrowing']
)
@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def reject_borrow_request(request, record_id):
    """
    PATCH /api/books/admin/borrow/{id}/reject/
    Rejects a pending borrow request. Admin only.
    """
    # Check if user is admin
    if request.user.role != 'admin':
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        borrow_record = BorrowRecord.objects.get(id=record_id)
    except BorrowRecord.DoesNotExist:
        return Response(
            {"detail": "Borrow record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        BorrowingService.reject_request(borrow_record)
        return Response(
            {"message": "Borrow request rejected."},
            status=status.HTTP_200_OK
        )
    except ValueError as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
