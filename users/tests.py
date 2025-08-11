from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationTests(APITestCase):
    """Tests for user registration endpoint."""
    
    def setUp(self):
        self.register_url = reverse('user-register')
        self.valid_payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }
    
    def test_register_user_success(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')
        self.assertEqual(User.objects.get().is_active, False)  # User should start inactive
        self.assertEqual(User.objects.get().role, 'member')  # Default role should be member
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username."""
        # Create a user first
        User.objects.create_user(username='testuser', email='other@example.com', password='password123')
        
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)  # No new user should be created
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        # Create a user first
        User.objects.create_user(username='otheruser', email='test@example.com', password='password123')
        
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)  # No new user should be created


class UserLoginTests(APITestCase):
    """Tests for user login endpoint."""
    
    def setUp(self):
        self.login_url = reverse('user-login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPassword123!',
            is_active=True  # User must be active to login
        )
    
    def test_login_success(self):
        """Test successful login."""
        payload = {
            'username': 'testuser',
            'password': 'StrongPassword123!'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_inactive_user(self):
        """Test login with inactive user."""
        # Set user to inactive
        self.user.is_active = False
        self.user.save()
        
        payload = {
            'username': 'testuser',
            'password': 'StrongPassword123!'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        payload = {
            'username': 'testuser',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminUserTests(APITestCase):
    """Tests for admin user endpoints."""
    
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            is_active=True,
            role='admin'
        )
        
        # Create regular user (inactive)
        self.regular_user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='MemberPass123!',
            is_active=False,
            role='member'
        )
        
        # URLs
        self.user_list_url = reverse('admin-user-list')
        self.user_approve_url = reverse('admin-user-approve', kwargs={'id': self.regular_user.id})
        
        # Authenticate admin
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_list_users(self):
        """Test listing all users as admin."""
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return both users
    
    def test_list_users_filtered(self):
        """Test listing users filtered by active status."""
        response = self.client.get(f'{self.user_list_url}?is_active=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should return only inactive user
        self.assertEqual(response.data[0]['username'], 'member')
    
    def test_approve_user(self):
        """Test approving a user registration."""
        response = self.client.patch(self.user_approve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user is now active
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.is_active)
    
    def test_non_admin_cannot_list_users(self):
        """Test that non-admin users cannot list all users."""
        # Authenticate as regular user
        self.regular_user.is_active = True
        self.regular_user.save()
        refresh = RefreshToken.for_user(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_non_admin_cannot_approve_users(self):
        """Test that non-admin users cannot approve registrations."""
        # Authenticate as regular user
        self.regular_user.is_active = True
        self.regular_user.save()
        refresh = RefreshToken.for_user(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create another inactive user
        another_user = User.objects.create_user(
            username='another',
            email='another@example.com',
            password='AnotherPass123!',
            is_active=False
        )
        
        approve_url = reverse('admin-user-approve', kwargs={'id': another_user.id})
        response = self.client.patch(approve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify user is still inactive
        another_user.refresh_from_db()
        self.assertFalse(another_user.is_active)
