from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Book, BorrowRecord
from .serializers import (
    BookSerializer, BorrowRequestSerializer, ReturnBookSerializer, 
    BorrowRecordSerializer
)
from .services import BorrowingService
from users.permissions import IsAdminUser


# Book Management Views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def book_list_create(request):
    """
    GET: Retrieves a list of all books. Supports searching.
    POST: Creates a new book (Admin only).
    """
    if request.method == 'GET':
        books = Book.objects.all()
        search = request.query_params.get('search', None)
        
        if search:
            books = books.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(genre__icontains=search)
            )
        
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Admin only
        if not (request.user.is_authenticated and request.user.role == 'admin'):
            return Response(
                {"error": "Admin access required"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def book_detail(request, book_id):
    """
    GET: Retrieves a single book by its ID.
    PUT: Updates all fields of a specific book (Admin only).
    DELETE: Deletes a book from the catalog (Admin only).
    """
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'GET':
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Admin only
        if not (request.user.is_authenticated and request.user.role == 'admin'):
            return Response(
                {"error": "Admin access required"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Admin only
        if not (request.user.is_authenticated and request.user.role == 'admin'):
            return Response(
                {"error": "Admin access required"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Borrowing Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def borrow_book(request):
    """
    Allows a member to submit a request to borrow a book.
    """
    serializer = BorrowRequestSerializer(data=request.data)
    if serializer.is_valid():
        try:
            book_id = serializer.validated_data['book_id']
            book = get_object_or_404(Book, id=book_id)
            
            borrow_record = BorrowingService.request_borrow(request.user, book)
            
            return Response(
                {"message": "Borrow request submitted successfully. Waiting for admin approval."},
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def return_book(request):
    """
    Allows a member to return a book they have borrowed.
    """
    serializer = ReturnBookSerializer(data=request.data)
    if serializer.is_valid():
        try:
            borrow_record_id = serializer.validated_data['borrow_record_id']
            borrow_record = get_object_or_404(BorrowRecord, id=borrow_record_id)
            
            # Check if the record belongs to the user
            if borrow_record.user != request.user:
                return Response(
                    {"error": "This record does not belong to you"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            BorrowingService.return_book(borrow_record)
            
            return Response(
                {"message": "Book returned successfully."},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin Borrowing Views
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_borrow_list(request):
    """
    Retrieves a list of all borrow records. Can be filtered by status.
    """
    borrow_records = BorrowRecord.objects.all().select_related('user', 'book')
    status_filter = request.query_params.get('status', None)
    
    if status_filter:
        borrow_records = borrow_records.filter(status=status_filter.upper())
    
    serializer = BorrowRecordSerializer(borrow_records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def approve_borrow_request(request, record_id):
    """
    Approves a pending borrow request.
    """
    try:
        borrow_record = get_object_or_404(BorrowRecord, id=record_id)
        BorrowingService.approve_request(borrow_record)
        
        return Response(
            {"message": "Borrow request approved."},
            status=status.HTTP_200_OK
        )
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def reject_borrow_request(request, record_id):
    """
    Rejects a pending borrow request.
    """
    try:
        borrow_record = get_object_or_404(BorrowRecord, id=record_id)
        BorrowingService.reject_request(borrow_record)
        
        return Response(
            {"message": "Borrow request rejected."},
            status=status.HTTP_200_OK
        )
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        ) 