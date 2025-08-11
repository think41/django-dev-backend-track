from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Book
from app.users.models import BookRequest, BorrowHistory
from app.authentication.permissions import IsApprovedUser
from .serializers import (
    BookSearchSerializer, 
    BookRequestSerializer, 
    BorrowHistorySerializer,
    BookReturnSerializer,
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_books(request):
    """
    Search for books by title, author, or genre
    """
    query = request.GET.get('q', '')
    title = request.GET.get('title', '')
    author = request.GET.get('author', '')
    genre = request.GET.get('genre', '')
    
    books = Book.objects.all()
    
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(genre__icontains=query)
        )
    
    if title:
        books = books.filter(title__icontains=title)
    
    if author:
        books = books.filter(author__icontains=author)
        
    if genre:
        books = books.filter(genre__icontains=genre)
    
    serializer = BookSearchSerializer(books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsApprovedUser])
def request_book(request):
    """
    Request to borrow a book
    """
    serializer = BookRequestSerializer(data=request.data)
    if serializer.is_valid():
        book_id = serializer.validated_data['book'].id
        
        # Check if book exists and has available copies
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if book.available_copies <= 0:
            return Response({'error': 'No copies available'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already has a pending/approved request for this book
        existing_request = BookRequest.objects.filter(
            user=request.user,
            book=book,
            status__in=['PENDING', 'APPROVED']
        ).exists()
        
        if existing_request:
            return Response(
                {'error': 'You already have a pending or approved request for this book'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the borrow request
        book_request = BookRequest.objects.create(
            user=request.user,
            book=book,
            request_date=timezone.now(),
            status='PENDING'
        )
        
        response_serializer = BookRequestSerializer(book_request)
        return Response({
            'message': 'Borrow request submitted successfully',
            'request': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsApprovedUser])
def return_book(request):
    """
    Return a borrowed book
    """
    serializer = BookReturnSerializer(data=request.data)
    if serializer.is_valid():
        book_request_id = serializer.validated_data['book_request_id']
        
        try:
            book_request = BookRequest.objects.get(
                id=book_request_id,
                user=request.user,
                status='APPROVED',
                return_date__isnull=True
            )
        except BookRequest.DoesNotExist:
            return Response(
                {'error': 'No active borrow record found for this request'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update the book request with return date
        book_request.return_date = timezone.now()
        book_request.save()
        
        # Add to borrow history
        BorrowHistory.objects.create(
            user=request.user,
            book=book_request.book,
            borrow_date=book_request.borrow_date,
            return_date=book_request.return_date
        )
        
        # Increase available copies
        book = book_request.book
        book.available_copies += 1
        book.save()
        
        return Response({
            'message': 'Book returned successfully',
            'return_date': book_request.return_date
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def borrowing_history(request):
    """
    View borrowing history for the authenticated user
    """
    history = BorrowHistory.objects.filter(user=request.user).order_by('-borrow_date')
    serializer = BorrowHistorySerializer(history, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def borrow_requests(request):
    """
    View all borrow requests for the authenticated user
    """
    requests = BookRequest.objects.filter(user=request.user).order_by('-request_date')
    serializer = BookRequestSerializer(requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
