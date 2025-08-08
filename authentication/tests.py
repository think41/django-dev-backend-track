from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AuthService

User = get_user_model()

class AuthServiceTestCase(TestCase):
    """Tests for AuthService model methods"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'user'
        }
    
    def test_register_user(self):
        user = AuthService.register_user(self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'user')
    
    def test_authenticate_user(self):
        user = AuthService.register_user(self.user_data)
        authenticated_user = AuthService.authenticate_user('testuser', 'testpass123')
        self.assertEqual(authenticated_user, user)
    
    def test_generate_jwt_tokens(self):
        user = AuthService.register_user(self.user_data)
        tokens = AuthService.generate_jwt_tokens(user)
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
    
    def test_register_user_with_invalid_password(self):
        invalid_data = self.user_data.copy()
        invalid_data['password'] = '123'  # Too short
        with self.assertRaises(Exception):
            AuthService.register_user(invalid_data)
    
    def test_authenticate_user_with_wrong_password(self):
        user = AuthService.register_user(self.user_data)
        authenticated_user = AuthService.authenticate_user('testuser', 'wrongpassword')
        self.assertIsNone(authenticated_user)
    
    def test_authenticate_nonexistent_user(self):
        authenticated_user = AuthService.authenticate_user('nonexistent', 'password')
        self.assertIsNone(authenticated_user)


class AuthenticationAPITestCase(APITestCase):
    """Tests for authentication API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth:register')
        self.login_url = reverse('auth:login')
        self.refresh_url = reverse('auth:refresh')
        self.logout_url = reverse('auth:logout')
        self.verify_url = reverse('auth:verify')
        
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'user'
        }
        
        self.valid_login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
    
    def test_register_user_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['role'], 'user')
    
    def test_register_user_with_invalid_data(self):
        """Test user registration with invalid data"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['password'] = '123'  # Too short
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_user_with_duplicate_username(self):
        """Test user registration with duplicate username"""
        # Create first user
        self.client.post(self.register_url, self.valid_user_data)
        
        # Try to create second user with same username
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['email'] = 'different@example.com'
        
        response = self.client.post(self.register_url, duplicate_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_user_with_invalid_role(self):
        """Test user registration with invalid role"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['role'] = 'invalid_role'
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_user_success(self):
        """Test successful user login"""
        # Register user first
        self.client.post(self.register_url, self.valid_user_data)
        
        # Login
        response = self.client.post(self.login_url, self.valid_login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_login_user_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_login_user_with_invalid_data(self):
        """Test login with invalid data format"""
        response = self.client.post(self.login_url, {
            'username': 'testuser'
            # Missing password
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_refresh_token_success(self):
        """Test successful token refresh"""
        # Register and login to get tokens
        self.client.post(self.register_url, self.valid_user_data)
        login_response = self.client.post(self.login_url, self.valid_login_data)
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Refresh token
        response = self.client.post(self.refresh_url, {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_refresh_token_with_invalid_token(self):
        """Test token refresh with invalid refresh token"""
        # Register and login to get access token for authentication
        self.client.post(self.register_url, self.valid_user_data)
        login_response = self.client.post(self.login_url, self.valid_login_data)
        access_token = login_response.data['access']
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.post(self.refresh_url, {
            'refresh': 'invalid_token'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_refresh_token_without_authentication(self):
        """Test token refresh without authentication"""
        response = self.client.post(self.refresh_url, {
            'refresh': 'some_token'
        })
        # Should fail because endpoint requires authentication
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)  # DRF returns 'detail' for authentication errors
    
    def test_logout_user_success(self):
        """Test successful user logout"""
        # Register and login to get tokens
        self.client.post(self.register_url, self.valid_user_data)
        login_response = self.client.post(self.login_url, self.valid_login_data)
        refresh_token = login_response.data['refresh']
        
        # Authenticate the client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')
        
        # Logout
        response = self.client.post(self.logout_url, {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_logout_user_with_invalid_token(self):
        """Test logout with invalid refresh token"""
        # Register and login to get access token for authentication
        self.client.post(self.register_url, self.valid_user_data)
        login_response = self.client.post(self.login_url, self.valid_login_data)
        
        # Authenticate the client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')
        
        # Logout with invalid token
        response = self.client.post(self.logout_url, {
            'refresh': 'invalid_token'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_logout_user_without_authentication(self):
        """Test logout without authentication"""
        response = self.client.post(self.logout_url, {
            'refresh': 'some_token'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_verify_token_success(self):
        """Test successful token verification"""
        # Register and login to get tokens
        self.client.post(self.register_url, self.valid_user_data)
        login_response = self.client.post(self.login_url, self.valid_login_data)
        access_token = login_response.data['access']
        
        # Authenticate the client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Verify token
        response = self.client.post(self.verify_url, {
            'token': access_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])
        self.assertIn('user_info', response.data)
        self.assertEqual(response.data['user_info']['username'], 'testuser')
    
    def test_verify_token_with_invalid_token(self):
        """Test token verification with invalid token"""
        # Register and login to get access token for authentication
        self.client.post(self.register_url, self.valid_user_data)
        login_response = self.client.post(self.login_url, self.valid_login_data)
        access_token = login_response.data['access']
        
        # Authenticate the client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Verify invalid token
        response = self.client.post(self.verify_url, {
            'token': 'invalid_token'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['valid'])
        self.assertIn('error', response.data)
    
    def test_verify_token_without_authentication(self):
        """Test token verification without authentication"""
        response = self.client.post(self.verify_url, {
            'token': 'some_token'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)  # DRF returns 'detail' for authentication errors
    
    def test_complete_authentication_flow(self):
        """Test complete authentication flow: register -> login -> refresh -> verify -> logout"""
        # 1. Register user
        register_response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
        # 2. Login user
        login_response = self.client.post(self.login_url, self.valid_login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']
        
        # 3. Authenticate client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # 4. Refresh token
        refresh_response = self.client.post(self.refresh_url, {
            'refresh': refresh_token
        })
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        new_access_token = refresh_response.data['access']
        
        # 5. Update client with new access token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        
        # 6. Verify token
        verify_response = self.client.post(self.verify_url, {
            'token': new_access_token
        })
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertTrue(verify_response.data['valid'])
        
        # 7. Logout
        logout_response = self.client.post(self.logout_url, {
            'refresh': refresh_token
        })
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
    
    def test_admin_user_registration(self):
        """Test admin user registration"""
        admin_data = self.valid_user_data.copy()
        admin_data['username'] = 'adminuser'
        admin_data['email'] = 'admin@example.com'
        admin_data['role'] = 'admin'
        
        response = self.client.post(self.register_url, admin_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['role'], 'admin')
    
    def test_user_registration_without_role(self):
        """Test user registration without specifying role (should default to 'user')"""
        user_data_without_role = self.valid_user_data.copy()
        user_data_without_role['username'] = 'defaultuser'
        user_data_without_role['email'] = 'default@example.com'
        del user_data_without_role['role']
        
        response = self.client.post(self.register_url, user_data_without_role)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['role'], 'user')
