"""
Views for the Books app.

This module contains all API views for book management, including
public search endpoints and admin CRUD operations.
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Book
from .serializers import (
    BookSerializer,
    BookSearchSerializer,
    BookCreateSerializer,
    BookUpdateSerializer,
    AdminBookListSerializer
)
from lms.users.permissions import IsAdmin


# Public Book Endpoints
class BookSearchView(generics.ListAPIView):
    """
    Public API endpoint for searching books.
    GET /api/books/search/
    
    Query Parameters:
        - title: Search by title (case-insensitive, partial match)
        - author: Search by author (case-insensitive, partial match)
        - genre: Filter by genre (case-insensitive, partial match)
        - available: Filter by availability (true/false)
    """
    serializer_class = BookSearchSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Book.objects.all()
        
        # Get query parameters
        title = self.request.query_params.get('title')
        author = self.request.query_params.get('author')
        genre = self.request.query_params.get('genre')
        available = self.request.query_params.get('available')
        
        # Apply filters
        if title:
            queryset = queryset.filter(title__icontains=title)
        
        if author:
            queryset = queryset.filter(author__icontains=author)
        
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        
        if available is not None:
            if available.lower() == 'true':
                queryset = queryset.filter(available_copies__gt=0)
            elif available.lower() == 'false':
                queryset = queryset.filter(available_copies=0)
        
        return queryset.order_by('title')


class BookDetailView(generics.RetrieveAPIView):
    """
    Public API endpoint for retrieving book details.
    GET /api/books/{id}/
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]


# Admin Book Management Endpoints
class AdminBookListView(generics.ListAPIView):
    """
    Admin API endpoint for viewing all books.
    GET /api/books/admin/
    """
    queryset = Book.objects.all().order_by('title')
    serializer_class = AdminBookListSerializer
    permission_classes = [IsAdmin]


class AdminBookCreateView(generics.CreateAPIView):
    """
    Admin API endpoint for adding new books.
    POST /api/books/admin/
    """
    queryset = Book.objects.all()
    serializer_class = BookCreateSerializer
    permission_classes = [IsAdmin]
    
    def create(self, request, *args, **kwargs):
        """Create a new book and return detailed information."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        book = serializer.save()
        
        # Return the created book with full details
        response_serializer = AdminBookListSerializer(book)
        return Response(
            {
                'message': 'Book created successfully',
                'book': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class AdminBookUpdateView(generics.UpdateAPIView):
    """
    Admin API endpoint for updating books.
    PUT/PATCH /api/books/admin/{id}/
    """
    queryset = Book.objects.all()
    serializer_class = BookUpdateSerializer
    permission_classes = [IsAdmin]
    
    def update(self, request, *args, **kwargs):
        """Update book and return updated information."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_book = serializer.save()
        
        # Return the updated book with full details
        response_serializer = AdminBookListSerializer(updated_book)
        return Response(
            {
                'message': 'Book updated successfully',
                'book': response_serializer.data
            }
        )


class AdminBookDeleteView(generics.DestroyAPIView):
    """
    Admin API endpoint for deleting books.
    DELETE /api/books/admin/{id}/
    """
    queryset = Book.objects.all()
    permission_classes = [IsAdmin]
    
    def destroy(self, request, *args, **kwargs):
        """Delete book with validation."""
        instance = self.get_object()
        
        # Check if book has any borrowed copies
        if instance.borrowed_copies > 0:
            return Response(
                {
                    'error': f'Cannot delete book with {instance.borrowed_copies} borrowed copies. '
                            'Please wait for all copies to be returned.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        book_info = {
            'id': instance.id,
            'title': instance.title,
            'author': instance.author
        }
        
        self.perform_destroy(instance)
        
        return Response(
            {
                'message': 'Book deleted successfully',
                'deleted_book': book_info
            },
            status=status.HTTP_204_NO_CONTENT
        )


# Combined Admin CRUD View (Alternative approach)
@api_view(['GET', 'POST'])
@permission_classes([IsAdmin])
def admin_book_list_create(request):
    """
    Admin API endpoint for listing and creating books.
    GET /api/books/admin/ - List all books
    POST /api/books/admin/ - Create new book
    """
    if request.method == 'GET':
        books = Book.objects.all().order_by('title')
        serializer = AdminBookListSerializer(books, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = BookCreateSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save()
            response_serializer = AdminBookListSerializer(book)
            return Response(
                {
                    'message': 'Book created successfully',
                    'book': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAdmin])
def admin_book_detail(request, pk):
    """
    Admin API endpoint for book detail operations.
    GET /api/books/admin/{id}/ - Get book details
    PUT/PATCH /api/books/admin/{id}/ - Update book
    DELETE /api/books/admin/{id}/ - Delete book
    """
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'GET':
        serializer = AdminBookListSerializer(book)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = BookUpdateSerializer(book, data=request.data, partial=partial)
        if serializer.is_valid():
            updated_book = serializer.save()
            response_serializer = AdminBookListSerializer(updated_book)
            return Response(
                {
                    'message': 'Book updated successfully',
                    'book': response_serializer.data
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Check if book has borrowed copies
        if book.borrowed_copies > 0:
            return Response(
                {
                    'error': f'Cannot delete book with {book.borrowed_copies} borrowed copies. '
                            'Please wait for all copies to be returned.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        book_info = {
            'id': book.id,
            'title': book.title,
            'author': book.author
        }
        
        book.delete()
        
        return Response(
            {
                'message': 'Book deleted successfully',
                'deleted_book': book_info
            },
            status=status.HTTP_204_NO_CONTENT
        )