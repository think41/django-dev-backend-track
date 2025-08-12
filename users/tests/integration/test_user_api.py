import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationAPITest(APITestCase):
    """
    Integration tests for user registration API endpoint.
    Tests user creation and validation.
    """
    
    def setUp(self):
        """
        Set up test data for user registration tests.
        """
        self.register_url = reverse('register')
        
        self.valid_user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        
        # Create an existing user for duplicate tests
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='ExistingPass123!'
        )
    
    def test_register_user_success(self):
        """
        Test successful user registration.
        """
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('User registered successfully', response.data['message'])
        
        # Check that user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Check that user is inactive by default
        user = User.objects.get(username='newuser')
        self.assertFalse(user.is_active)
        self.assertEqual(user.role, 'member')
    
    def test_register_with_duplicate_username(self):
        """
        Test registration with duplicate username.
        """
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['username'] = 'existinguser'
        
        response = self.client.post(self.register_url, duplicate_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
    
    def test_register_with_duplicate_email(self):
        """
        Test registration with duplicate email.
        """
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['email'] = 'existing@example.com'
        
        response = self.client.post(self.register_url, duplicate_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_register_with_mismatched_passwords(self):
        """
        Test registration with mismatched passwords.
        """
        invalid_data = self.valid_user_data.copy()
        invalid_data['password2'] = 'DifferentPass123!'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)
    
    def test_register_with_short_password(self):
        """
        Test registration with too short password.
        """
        invalid_data = self.valid_user_data.copy()
        invalid_data['password'] = 'short'
        invalid_data['password2'] = 'short'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class UserLoginAPITest(APITestCase):
    """
    Integration tests for user login API endpoint.
    Tests token generation and validation.
    """
    
    def setUp(self):
        """
        Set up test data for user login tests.
        """
        self.login_url = reverse('token_obtain_pair')
        
        # Create active user
        self.active_user = User.objects.create_user(
            username='activeuser',
            email='active@example.com',
            password='ActivePass123!',
            is_active=True
        )
        
        # Create inactive user
        self.inactive_user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='InactivePass123!',
            is_active=False
        )
    
    def test_login_success(self):
        """
        Test successful login with valid credentials.
        """
        data = {
            'username': 'activeuser',
            'password': 'ActivePass123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_with_inactive_user(self):
        """
        Test login with inactive user.
        """
        data = {
            'username': 'inactiveuser',
            'password': 'InactivePass123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_with_invalid_credentials(self):
        """
        Test login with invalid credentials.
        """
        data = {
            'username': 'activeuser',
            'password': 'WrongPass123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserListAPITest(APITestCase):
    """
    Integration tests for user listing API endpoint.
    Tests permissions and filtering.
    """
    
    def setUp(self):
        """
        Set up test data for user listing tests.
        """
        self.user_list_url = reverse('user-list')
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            is_active=True,
            role='admin'
        )
        
        # Create librarian user
        self.librarian_user = User.objects.create_user(
            username='librarian',
            email='librarian@example.com',
            password='LibrarianPass123!',
            is_active=True,
            role='librarian'
        )
        
        # Create member user
        self.member_user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='MemberPass123!',
            is_active=True,
            role='member'
        )
        
        # Create inactive user
        self.inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='InactivePass123!',
            is_active=False,
            role='member'
        )
    
    def authenticate_as_admin(self):
        """Helper method to authenticate as admin"""
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def authenticate_as_librarian(self):
        """Helper method to authenticate as librarian"""
        refresh = RefreshToken.for_user(self.librarian_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def authenticate_as_member(self):
        """Helper method to authenticate as member"""
        refresh = RefreshToken.for_user(self.member_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_list_users_as_admin(self):
        """
        Test listing all users as admin.
        """
        self.authenticate_as_admin()
        
        response = self.client.get(self.user_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # All users
    
    def test_list_users_as_librarian(self):
        """
        Test listing all users as librarian.
        """
        self.authenticate_as_librarian()
        
        response = self.client.get(self.user_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # All users
    
    def test_list_users_as_member(self):
        """
        Test listing all users as member (should be forbidden).
        """
        self.authenticate_as_member()
        
        response = self.client.get(self.user_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_users_unauthenticated(self):
        """
        Test listing all users without authentication.
        """
        response = self.client.get(self.user_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_filter_users_by_role(self):
        """
        Test filtering users by role.
        """
        self.authenticate_as_admin()
        
        # Filter by member role
        response = self.client.get(f"{self.user_list_url}?role=member")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # member and inactive
        
        # Filter by admin role
        response = self.client.get(f"{self.user_list_url}?role=admin")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # admin only
    
    def test_filter_users_by_active_status(self):
        """
        Test filtering users by active status.
        """
        self.authenticate_as_admin()
        
        # Filter by active status
        response = self.client.get(f"{self.user_list_url}?is_active=true")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # admin, librarian, member
        
        # Filter by inactive status
        response = self.client.get(f"{self.user_list_url}?is_active=false")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # inactive only


class UserApprovalAPITest(APITestCase):
    """
    Integration tests for user approval API endpoint.
    Tests approval and rejection of users.
    """
    
    def setUp(self):
        """
        Set up test data for user approval tests.
        """
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            is_active=True,
            role='admin'
        )
        
        # Create librarian user
        self.librarian_user = User.objects.create_user(
            username='librarian',
            email='librarian@example.com',
            password='LibrarianPass123!',
            is_active=True,
            role='librarian'
        )
        
        # Create member user
        self.member_user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='MemberPass123!',
            is_active=True,
            role='member'
        )
        
        # Create inactive user
        self.inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='InactivePass123!',
            is_active=False,
            role='member'
        )
        
        # URLs
        self.approval_url = reverse('user-approval', kwargs={'pk': self.inactive_user.pk})
    
    def authenticate_as_admin(self):
        """Helper method to authenticate as admin"""
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def authenticate_as_librarian(self):
        """Helper method to authenticate as librarian"""
        refresh = RefreshToken.for_user(self.librarian_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def authenticate_as_member(self):
        """Helper method to authenticate as member"""
        refresh = RefreshToken.for_user(self.member_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_approve_user_as_admin(self):
        """
        Test approving a user as admin.
        """
        self.authenticate_as_admin()
        
        data = {
            'is_active': True
        }
        
        response = self.client.patch(self.approval_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approved successfully', response.data['message'].lower())
        
        # Check that user was activated
        self.inactive_user.refresh_from_db()
        self.assertTrue(self.inactive_user.is_active)
    
    def test_reject_user_as_admin(self):
        """
        Test rejecting an active user as admin.
        """
        # First approve the user
        self.inactive_user.is_active = True
        self.inactive_user.save()
        
        self.authenticate_as_admin()
        
        data = {
            'is_active': False
        }
        
        response = self.client.patch(self.approval_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('deactivated successfully', response.data['message'].lower())
        
        # Check that user was deactivated
        self.inactive_user.refresh_from_db()
        self.assertFalse(self.inactive_user.is_active)
    
    def test_approve_user_as_librarian(self):
        """
        Test approving a user as librarian.
        """
        self.authenticate_as_librarian()
        
        data = {
            'is_active': True
        }
        
        response = self.client.patch(self.approval_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approved successfully', response.data['message'].lower())
        
        # Check that user was activated
        self.inactive_user.refresh_from_db()
        self.assertTrue(self.inactive_user.is_active)
    
    def test_approve_user_as_member(self):
        """
        Test approving a user as member (should be forbidden).
        """
        self.authenticate_as_member()
        
        data = {
            'is_active': True
        }
        
        response = self.client.patch(self.approval_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Check that user was not activated
        self.inactive_user.refresh_from_db()
        self.assertFalse(self.inactive_user.is_active)
