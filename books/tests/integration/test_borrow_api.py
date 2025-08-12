import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book, BorrowRecord
from books.tests.fixtures import UserFixture, BookFixture, BorrowFixture
from users.tests.fixtures import AuthFixture

User = get_user_model()


class BorrowAPITest(APITestCase):
    """
    Integration tests for Borrow API endpoints.
    Tests borrow request, approval, rejection, and return operations with proper permissions.
    
    This test suite verifies that:
    1. Users can request to borrow books with available copies
    2. Librarians and admins can approve or reject borrow requests
    3. Members can return borrowed books
    4. Proper permissions are enforced for all operations
    5. Book quantities are updated correctly during the borrowing process
    """
    
    def setUp(self):
        """
        Set up test data for Borrow API tests using fixtures.
        """
        # Create users with different roles
        self.admin_user = UserFixture.create_admin_user()
        self.librarian_user = UserFixture.create_librarian_user()
        self.member_user = UserFixture.create_member_user()
        self.inactive_user = UserFixture.create_inactive_user()
        
        # Create sample books
        self.book1 = BookFixture.create_book(
            title='Test Book 1',
            author='Test Author 1',
            genre='Fiction',
            isbn='1234567890123',
            quantity=5
        )
        
        self.book2 = BookFixture.create_book(
            title='Test Book 2',
            author='Test Author 2',
            genre='Non-Fiction',
            isbn='9876543210987',
            quantity=0  # No copies available
        )
        
        # Create borrow records using fixtures
        self.pending_borrow = BorrowFixture.create_pending_borrow(
            user=self.member_user,
            book=self.book1
        )
        
        self.approved_borrow = BorrowFixture.create_approved_borrow(
            user=self.member_user,
            book=self.book1
        )
        
        # URLs
        self.borrow_request_url = reverse('borrow-request')
        self.book_return_url = reverse('book-return')
        self.admin_borrow_list_url = reverse('admin-borrow-list')
        self.admin_approve_url = reverse('admin-borrow-approve', kwargs={'id': self.pending_borrow.pk})
        self.admin_reject_url = reverse('admin-borrow-reject', kwargs={'id': self.pending_borrow.pk})
    
    def authenticate_as_admin(self):
        """Helper method to authenticate as admin"""
        AuthFixture.authenticate_client(self.client, self.admin_user)
    
    def authenticate_as_member(self):
        """Helper method to authenticate as member"""
        AuthFixture.authenticate_client(self.client, self.member_user)
    
    def authenticate_as_another_member(self):
        """Helper method to authenticate as another member"""
        another_member = UserFixture.create_member_user()
        AuthFixture.authenticate_client(self.client, another_member)
    
    def test_request_borrow_success(self):
        """
        Test successful borrow request creation.
        """
        self.authenticate_as_another_member()
        
        data = {
            'book_id': self.book1.id
        }
        
        response = self.client.post(self.borrow_request_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Borrow request submitted successfully', response.data['message'])
        
        # Check that a new borrow record was created
        self.assertTrue(BorrowRecord.objects.filter(
            user=self.another_member,
            book=self.available_book,
            status='PENDING'
        ).exists())
    
    def test_request_borrow_unavailable_book(self):
        """
        Test borrow request for unavailable book.
        """
        self.authenticate_as_member()
        
        data = {
            'book_id': self.unavailable_book.id
        }
        
        response = self.client.post(self.borrow_request_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not available', response.data['error'].lower())
    
    def test_request_borrow_existing_request(self):
        """
        Test borrow request for book with existing request.
        """
        self.authenticate_as_member()
        
        data = {
            'book_id': self.available_book.id
        }
        
        response = self.client.post(self.borrow_request_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already have a pending or approved request', response.data['error'].lower())
    
    def test_return_book_success(self):
        """
        Test successful return of borrowed book.
        """
        self.authenticate_as_member()
        
        data = {
            'borrow_record_id': self.approved_borrow.id
        }
        
        response = self.client.post(self.book_return_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Book returned successfully', response.data['message'])
        
        # Check that the borrow record was updated
        self.approved_borrow.refresh_from_db()
        self.assertEqual(self.approved_borrow.status, 'RETURNED')
        self.assertIsNotNone(self.approved_borrow.return_date)
        
        # Check that the book quantity was incremented
        self.available_book.refresh_from_db()
        self.assertEqual(self.available_book.quantity, 6)  # 5 + 1
    
    def test_return_book_not_borrowed(self):
        """
        Test return of book that is not borrowed by the user.
        """
        self.authenticate_as_another_member()
        
        data = {
            'borrow_record_id': self.approved_borrow.id
        }
        
        response = self.client.post(self.book_return_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('does not belong to you', response.data['error'])
    
    def test_admin_list_borrow_records(self):
        """
        Test listing all borrow records as admin.
        """
        self.authenticate_as_admin()
        
        response = self.client.get(self.admin_borrow_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_admin_filter_borrow_records(self):
        """
        Test filtering borrow records by status.
        """
        self.authenticate_as_admin()
        
        # Filter by PENDING status
        response = self.client.get(f"{self.admin_borrow_list_url}?status=PENDING")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'PENDING')
        
        # Filter by APPROVED status
        response = self.client.get(f"{self.admin_borrow_list_url}?status=APPROVED")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'APPROVED')
    
    def test_admin_approve_borrow_request(self):
        """
        Test approving a borrow request as admin.
        """
        self.authenticate_as_admin()
        
        initial_quantity = self.available_book.quantity
        
        response = self.client.patch(self.admin_approve_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approved successfully', response.data['message'].lower())
        
        # Check that the borrow record was updated
        self.pending_borrow.refresh_from_db()
        self.assertEqual(self.pending_borrow.status, 'APPROVED')
        self.assertIsNotNone(self.pending_borrow.borrow_date)
        self.assertIsNotNone(self.pending_borrow.due_date)
        
        # Check that the book quantity was decremented
        self.available_book.refresh_from_db()
        self.assertEqual(self.available_book.quantity, initial_quantity - 1)
    
    def test_admin_reject_borrow_request(self):
        """
        Test rejecting a borrow request as admin.
        """
        # Create a new pending borrow for this test
        new_pending = BorrowRecord.objects.create(
            user=self.another_member,
            book=self.available_book,
            status='PENDING'
        )
        
        reject_url = reverse('admin-borrow-reject', kwargs={'id': new_pending.pk})
        
        self.authenticate_as_admin()
        
        initial_quantity = self.available_book.quantity
        
        response = self.client.patch(reject_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rejected', response.data['message'].lower())
        
        # Check that the borrow record was updated
        new_pending.refresh_from_db()
        self.assertEqual(new_pending.status, 'REJECTED')
        
        # Check that the book quantity was not changed
        self.available_book.refresh_from_db()
        self.assertEqual(self.available_book.quantity, initial_quantity)
    
    def test_member_cannot_access_admin_endpoints(self):
        """
        Test that members cannot access admin borrowing endpoints.
        """
        self.authenticate_as_member()
        
        # Try to list all borrow records
        response = self.client.get(self.admin_borrow_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to approve a borrow request
        response = self.client.patch(self.admin_approve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to reject a borrow request
        response = self.client.patch(self.admin_reject_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
