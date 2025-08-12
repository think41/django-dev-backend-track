import pytest
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from books.models import Book, Reservation

User = get_user_model()


class ReservationAPITest(APITestCase):
    """Integration tests for Book reservation API endpoints."""
    
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
        
        # Create books
        self.available_book = Book.objects.create(
            title='Available Book', author='Test Author',
            genre='Fiction', quantity=5
        )
        self.unavailable_book = Book.objects.create(
            title='Unavailable Book', author='Test Author',
            genre='Non-Fiction', quantity=0
        )
        
        # Create reservations
        self.pending_reservation = Reservation.objects.create(
            user=self.member_user, book=self.unavailable_book,
            status='PENDING', reservation_date=timezone.now().date()
        )
        
        # URLs
        self.reservation_create_url = reverse('reservation-create')
        self.reservation_cancel_url = reverse('reservation-cancel')
        self.user_reservation_list_url = reverse('user-reservation-list')
        self.admin_reservation_list_url = reverse('admin-reservation-list')
    
    def authenticate_as_admin(self):
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def authenticate_as_member(self):
        refresh = RefreshToken.for_user(self.member_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def authenticate_as_another_member(self):
        refresh = RefreshToken.for_user(self.another_member)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_create_reservation_success(self):
        """Test successful reservation creation."""
        self.authenticate_as_another_member()
        
        data = {'book_id': self.unavailable_book.id}
        response = self.client.post(self.reservation_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Reservation created successfully', response.data['message'])
        
        # Check that a new reservation was created
        self.assertTrue(Reservation.objects.filter(
            user=self.another_member,
            book=self.unavailable_book,
            status='PENDING'
        ).exists())
    
    def test_create_reservation_available_book(self):
        """Test reservation for available book (should fail)."""
        self.authenticate_as_member()
        
        data = {'book_id': self.available_book.id}
        response = self.client.post(self.reservation_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('available for borrowing', response.data['error'].lower())
    
    def test_cancel_reservation_success(self):
        """Test successful cancellation of reservation."""
        self.authenticate_as_member()
        
        data = {'reservation_id': self.pending_reservation.id}
        response = self.client.post(self.reservation_cancel_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('cancelled successfully', response.data['message'].lower())
        
        # Check that the reservation was updated
        self.pending_reservation.refresh_from_db()
        self.assertEqual(self.pending_reservation.status, 'CANCELLED')
    
    def test_cancel_reservation_not_owned(self):
        """Test cancellation of reservation not owned by user."""
        self.authenticate_as_another_member()
        
        data = {'reservation_id': self.pending_reservation.id}
        response = self.client.post(self.reservation_cancel_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('does not belong to you', response.data['error'])
    
    def test_user_list_reservations(self):
        """Test listing user's reservations."""
        self.authenticate_as_member()
        
        response = self.client.get(self.user_reservation_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'PENDING')
    
    def test_admin_list_reservations(self):
        """Test listing all reservations as admin."""
        self.authenticate_as_admin()
        
        response = self.client.get(self.admin_reservation_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_admin_filter_reservations(self):
        """Test filtering reservations by status."""
        self.authenticate_as_admin()
        
        # Create a cancelled reservation
        Reservation.objects.create(
            user=self.another_member,
            book=self.unavailable_book,
            status='CANCELLED',
            reservation_date=timezone.now().date()
        )
        
        # Filter by PENDING status
        response = self.client.get(f"{self.admin_reservation_list_url}?status=PENDING")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'PENDING')
        
        # Filter by CANCELLED status
        response = self.client.get(f"{self.admin_reservation_list_url}?status=CANCELLED")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'CANCELLED')
    
    def test_member_cannot_access_admin_endpoints(self):
        """Test that members cannot access admin reservation endpoints."""
        self.authenticate_as_member()
        
        response = self.client.get(self.admin_reservation_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
