import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from books.models import Book, BorrowRecord, Fine

User = get_user_model()


class FineAPITest(APITestCase):
    """Integration tests for Fine API endpoints."""
    
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin', email='admin@example.com',
            password='AdminPass123!', is_active=True, role='admin'
        )
        self.member_user = User.objects.create_user(
            username='member', email='member@example.com',
            password='MemberPass123!', is_active=True, role='member'
        )
        self.another_member = User.objects.create_user(
            username='another', email='another@example.com',
            password='AnotherPass123!', is_active=True, role='member'
        )
        
        # Create book
        self.book = Book.objects.create(
            title='Test Book', author='Test Author',
            genre='Fiction', quantity=5
        )
        
        # Create borrow record with overdue return
        self.overdue_borrow = BorrowRecord.objects.create(
            user=self.member_user, book=self.book,
            status='RETURNED',
            borrow_date=timezone.now().date() - timedelta(days=20),
            due_date=timezone.now().date() - timedelta(days=6),
            return_date=timezone.now().date()
        )
        
        # Create fine
        self.fine = Fine.objects.create(
            borrow_record=self.overdue_borrow,
            user=self.member_user,
            amount=Decimal('3.00'),
            reason='Overdue return',
            status='PENDING',
            days_overdue=6
        )
        
        # Create another borrow record for fine creation test
        self.another_overdue_borrow = BorrowRecord.objects.create(
            user=self.another_member, book=self.book,
            status='RETURNED',
            borrow_date=timezone.now().date() - timedelta(days=25),
            due_date=timezone.now().date() - timedelta(days=11),
            return_date=timezone.now().date()
        )
        
        # URLs
        self.user_fine_list_url = reverse('user-fine-list')
        self.admin_fine_list_url = reverse('admin-fine-list')
        self.fine_payment_url = reverse('fine-payment', kwargs={'id': self.fine.pk})
        self.fine_create_url = reverse('admin-fine-create')
    
    def authenticate_as_admin(self):
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def authenticate_as_member(self):
        refresh = RefreshToken.for_user(self.member_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def authenticate_as_another_member(self):
        refresh = RefreshToken.for_user(self.another_member)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_user_list_fines(self):
        """Test listing user's fines."""
        self.authenticate_as_member()
        
        response = self.client.get(self.user_fine_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount'], '3.00')
        self.assertEqual(response.data[0]['status'], 'PENDING')
    
    def test_admin_list_fines(self):
        """Test listing all fines as admin."""
        self.authenticate_as_admin()
        
        response = self.client.get(self.admin_fine_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount'], '3.00')
    
    def test_admin_filter_fines(self):
        """Test filtering fines by status."""
        self.authenticate_as_admin()
        
        # Create a paid fine
        Fine.objects.create(
            borrow_record=self.another_overdue_borrow,
            user=self.another_member,
            amount=Decimal('5.50'),
            reason='Overdue return',
            status='PAID',
            days_overdue=11
        )
        
        # Filter by PENDING status
        response = self.client.get(f"{self.admin_fine_list_url}?status=PENDING")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'PENDING')
        
        # Filter by PAID status
        response = self.client.get(f"{self.admin_fine_list_url}?status=PAID")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'PAID')
    
    def test_pay_fine_success(self):
        """Test successful payment of fine."""
        self.authenticate_as_member()
        
        response = self.client.patch(self.fine_payment_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('paid successfully', response.data['message'].lower())
        
        # Check that the fine was updated
        self.fine.refresh_from_db()
        self.assertEqual(self.fine.status, 'PAID')
    
    def test_pay_fine_not_owned(self):
        """Test payment of fine not owned by user."""
        self.authenticate_as_another_member()
        
        response = self.client.patch(self.fine_payment_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('does not belong to you', response.data['error'])
    
    def test_admin_create_fine(self):
        """Test creating a fine as admin."""
        self.authenticate_as_admin()
        
        data = {
            'borrow_record_id': self.another_overdue_borrow.id,
            'amount': '5.50',
            'reason': 'Manual fine for damaged book',
            'days_overdue': 11
        }
        
        response = self.client.post(self.fine_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('created successfully', response.data['message'].lower())
        
        # Check that a new fine was created
        self.assertTrue(Fine.objects.filter(
            borrow_record=self.another_overdue_borrow,
            amount=Decimal('5.50'),
            reason='Manual fine for damaged book'
        ).exists())
    
    def test_member_cannot_create_fine(self):
        """Test that members cannot create fines."""
        self.authenticate_as_member()
        
        data = {
            'borrow_record_id': self.another_overdue_borrow.id,
            'amount': '5.50',
            'reason': 'Manual fine for damaged book',
            'days_overdue': 11
        }
        
        response = self.client.post(self.fine_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_member_cannot_access_admin_endpoints(self):
        """Test that members cannot access admin fine endpoints."""
        self.authenticate_as_member()
        
        response = self.client.get(self.admin_fine_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
