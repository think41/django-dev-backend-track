from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Book, BorrowRecord
from .services import BorrowingService

User = get_user_model()


class BookCatalogTests(APITestCase):
    """Tests for book catalog endpoints."""
    
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            is_active=True,
            role='admin'
        )
        
        # Create member user
        self.member_user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='MemberPass123!',
            is_active=True,
            role='member'
        )
        
        # Create sample book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Fiction',
            quantity=5
        )
        
        # URLs
        self.book_list_url = reverse('book-list')
        self.book_detail_url = reverse('book-detail', kwargs={'pk': self.book.pk})
        
        # Authenticate as admin by default
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_list_books(self):
        """Test listing all books."""
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Book')
    
    def test_search_books(self):
        """Test searching books by title."""
        # Create another book
        Book.objects.create(
            title='Another Book',
            author='Another Author',
            genre='Non-Fiction',
            quantity=3
        )
        
        response = self.client.get(f'{self.book_list_url}?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Book')
    
    def test_create_book_as_admin(self):
        """Test creating a book as admin."""
        payload = {
            'title': 'New Book',
            'author': 'New Author',
            'genre': 'Mystery',
            'quantity': 10
        }
        response = self.client.post(self.book_list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(Book.objects.filter(title='New Book').count(), 1)
    
    def test_create_book_as_member_forbidden(self):
        """Test that members cannot create books."""
        # Authenticate as member
        refresh = RefreshToken.for_user(self.member_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        payload = {
            'title': 'Member Book',
            'author': 'Member Author',
            'genre': 'Fantasy',
            'quantity': 2
        }
        response = self.client.post(self.book_list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 1)  # No new book created
    
    def test_update_book_as_admin(self):
        """Test updating a book as admin."""
        payload = {
            'title': 'Updated Book',
            'author': 'Updated Author',
            'genre': 'Fiction',
            'quantity': 7
        }
        response = self.client.put(self.book_detail_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify book was updated
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Updated Book')
        self.assertEqual(self.book.quantity, 7)
    
    def test_delete_book_as_admin(self):
        """Test deleting a book as admin."""
        response = self.client.delete(self.book_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)


class BorrowingTests(APITestCase):
    """Tests for book borrowing endpoints."""
    
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            is_active=True,
            role='admin'
        )
        
        # Create member user
        self.member_user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='MemberPass123!',
            is_active=True,
            role='member'
        )
        
        # Create sample book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Fiction',
            quantity=5
        )
        
        # URLs
        self.borrow_request_url = reverse('borrow-request')
        self.book_return_url = reverse('book-return')
        self.admin_borrow_list_url = reverse('admin-borrow-list')
        
        # Authenticate as member by default
        refresh = RefreshToken.for_user(self.member_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_request_borrow_as_member(self):
        """Test requesting to borrow a book as a member."""
        payload = {
            'book': self.book.id
        }
        response = self.client.post(self.borrow_request_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify borrow record was created
        self.assertEqual(BorrowRecord.objects.count(), 1)
        borrow_record = BorrowRecord.objects.first()
        self.assertEqual(borrow_record.user, self.member_user)
        self.assertEqual(borrow_record.book, self.book)
        self.assertEqual(borrow_record.status, 'PENDING')
    
    def test_request_borrow_unavailable_book(self):
        """Test requesting to borrow a book with quantity 0."""
        # Set book quantity to 0
        self.book.quantity = 0
        self.book.save()
        
        payload = {
            'book': self.book.id
        }
        response = self.client.post(self.borrow_request_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(BorrowRecord.objects.count(), 0)  # No borrow record created
    
    def test_return_book(self):
        """Test returning a borrowed book."""
        # Create an approved borrow record
        borrow_service = BorrowingService()
        borrow_record = borrow_service.request_borrow(self.member_user, self.book)
        borrow_service.approve_request(borrow_record.id)
        
        payload = {
            'borrow_record_id': borrow_record.id
        }
        response = self.client.post(self.book_return_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify borrow record was updated
        borrow_record.refresh_from_db()
        self.assertEqual(borrow_record.status, 'RETURNED')
        
        # Verify book quantity was incremented
        self.book.refresh_from_db()
        self.assertEqual(self.book.quantity, 5)  # Back to original quantity
    
    def test_return_book_not_borrowed(self):
        """Test returning a book that is not borrowed by the user."""
        # Create a borrow record for another user
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='OtherPass123!',
            is_active=True,
            role='member'
        )
        
        borrow_service = BorrowingService()
        borrow_record = borrow_service.request_borrow(other_user, self.book)
        borrow_service.approve_request(borrow_record.id)
        
        payload = {
            'borrow_record_id': borrow_record.id
        }
        response = self.client.post(self.book_return_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify borrow record was not updated
        borrow_record.refresh_from_db()
        self.assertEqual(borrow_record.status, 'APPROVED')  # Still approved, not returned


class AdminBorrowingTests(APITestCase):
    """Tests for admin borrowing endpoints."""
    
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            is_active=True,
            role='admin'
        )
        
        # Create member user
        self.member_user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='MemberPass123!',
            is_active=True,
            role='member'
        )
        
        # Create sample book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Fiction',
            quantity=5
        )
        
        # Create a pending borrow request
        borrow_service = BorrowingService()
        self.borrow_record = borrow_service.request_borrow(self.member_user, self.book)
        
        # URLs
        self.admin_borrow_list_url = reverse('admin-borrow-list')
        self.admin_approve_url = reverse('admin-borrow-approve', kwargs={'id': self.borrow_record.id})
        self.admin_reject_url = reverse('admin-borrow-reject', kwargs={'id': self.borrow_record.id})
        
        # Authenticate as admin
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_list_borrow_records(self):
        """Test listing all borrow records as admin."""
        response = self.client.get(self.admin_borrow_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'PENDING')
    
    def test_filter_borrow_records(self):
        """Test filtering borrow records by status."""
        # Create another borrow record and approve it
        borrow_service = BorrowingService()
        book2 = Book.objects.create(title='Book 2', author='Author 2', genre='Fiction', quantity=3)
        borrow_record2 = borrow_service.request_borrow(self.member_user, book2)
        borrow_service.approve_request(borrow_record2.id)
        
        # Filter by APPROVED status
        response = self.client.get(f'{self.admin_borrow_list_url}?status=APPROVED')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'APPROVED')
    
    def test_approve_borrow_request(self):
        """Test approving a borrow request as admin."""
        response = self.client.patch(self.admin_approve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify borrow record was updated
        self.borrow_record.refresh_from_db()
        self.assertEqual(self.borrow_record.status, 'APPROVED')
        
        # Verify book quantity was decremented
        self.book.refresh_from_db()
        self.assertEqual(self.book.quantity, 4)
    
    def test_reject_borrow_request(self):
        """Test rejecting a borrow request as admin."""
        response = self.client.patch(self.admin_reject_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify borrow record was updated
        self.borrow_record.refresh_from_db()
        self.assertEqual(self.borrow_record.status, 'REJECTED')
        
        # Verify book quantity was not changed
        self.book.refresh_from_db()
        self.assertEqual(self.book.quantity, 5)  # Still the same
    
    def test_member_cannot_access_admin_endpoints(self):
        """Test that members cannot access admin borrowing endpoints."""
        # Authenticate as member
        refresh = RefreshToken.for_user(self.member_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Try to list all borrow records
        response = self.client.get(self.admin_borrow_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to approve a borrow request
        response = self.client.patch(self.admin_approve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to reject a borrow request
        response = self.client.patch(self.admin_reject_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
