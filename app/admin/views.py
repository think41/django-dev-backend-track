from django.shortcuts import render
from .serializers import AdminUserListSerializer, UserApprovalSerializer
from app.authentication.permissions import IsAdminUser, IsApprovedUser
from .serializers import (
    BookSerializer,
    AdminBookRequestSerializer,
    BookRequestActionSerializer
)

# Create your views here.

# Admin-only views
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_users_list(request):
    """
    Admin: View all users
    """
    users = User.objects.all().order_by('-created_at')
    serializer = AdminUserListSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_approve_user(request):
    """
    Admin: Approve or disapprove member registration
    """
    serializer = UserApprovalSerializer(data=request.data)
    if serializer.is_valid():
        user_id = serializer.validated_data['user_id']
        approve = serializer.validated_data['approve']
        
        try:
            user = User.objects.get(id=user_id, role='Member')
        except User.DoesNotExist:
            return Response(
                {'error': 'Member user not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        user.is_approved = approve
        user.save()
        
        message = f"User {'approved' if approve else 'disapproved'} successfully"
        
        response_serializer = AdminUserListSerializer(user)
        return Response({
            'message': message,
            'user': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Admin-only views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_books(request):
    """
    Admin: List all books or create a new book
    """
    if request.method == 'GET':
        books = Book.objects.all().order_by('title')
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Book created successfully',
                'book': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_book_detail(request, book_id):
    """
    Admin: Retrieve, update, or delete a specific book
    """
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Book updated successfully',
                'book': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        book.delete()
        return Response({
            'message': 'Book deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_borrow_records(request):
    """
    Admin: View all borrow records with optional status filtering
    """
    status_filter = request.GET.get('status', '')
    
    records = BookRequest.objects.all().order_by('-request_date')
    
    if status_filter and status_filter.upper() in ['PENDING', 'APPROVED', 'REJECTED']:
        records = records.filter(status=status_filter.upper())
    
    serializer = AdminBookRequestSerializer(records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_approve_reject_request(request):
    """
    Admin: Approve or reject a borrow request
    """
    serializer = BookRequestActionSerializer(data=request.data)
    if serializer.is_valid():
        request_id = serializer.validated_data['request_id']
        action = serializer.validated_data['action']
        
        try:
            book_request = BookRequest.objects.get(id=request_id, status='PENDING')
        except BookRequest.DoesNotExist:
            return Response(
                {'error': 'Pending borrow request not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if action == 'approve':
            # Check if book has available copies
            if book_request.book.available_copies <= 0:
                return Response(
                    {'error': 'No copies available for this book'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Approve the request
            book_request.status = 'APPROVED'
            book_request.borrow_date = timezone.now()
            book_request.save()
            
            # Decrease available copies
            book = book_request.book
            book.available_copies -= 1
            book.save()
            
            message = 'Borrow request approved successfully'
            
        else:  # reject
            book_request.status = 'REJECTED'
            book_request.save()
            message = 'Borrow request rejected'
        
        response_serializer = AdminBookRequestSerializer(book_request)
        return Response({
            'message': message,
            'request': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
