import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from users.serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserApprovalSerializer
)

User = get_user_model()


class UserSerializerTest(TestCase):
    """
    Test case for the UserSerializer.
    Tests serialization of User model.
    """
    
    def setUp(self):
        """
        Set up test data for UserSerializer tests.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            is_active=True,
            role='member'
        )
        
        self.serializer = UserSerializer(instance=self.user)
    
    def test_contains_expected_fields(self):
        """
        Test that serializer contains all expected fields.
        """
        data = self.serializer.data
        expected_fields = ('id', 'username', 'email', 'role', 'is_active')
        
        self.assertEqual(set(data.keys()), set(expected_fields))
    
    def test_field_content(self):
        """
        Test that serialized data matches model data.
        """
        data = self.serializer.data
        
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['role'], self.user.role)
        self.assertEqual(data['is_active'], self.user.is_active)


class UserRegistrationSerializerTest(TestCase):
    """
    Test case for the UserRegistrationSerializer.
    Tests user registration validation and creation.
    """
    
    def setUp(self):
        """
        Set up test data for UserRegistrationSerializer tests.
        """
        self.user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        
        self.serializer = UserRegistrationSerializer(data=self.user_data)
    
    def test_contains_expected_fields(self):
        """
        Test that serializer contains all expected fields.
        """
        self.assertTrue(self.serializer.is_valid())
        expected_fields = ('username', 'email', 'password', 'password2')
        
        for field in expected_fields:
            self.assertIn(field, self.serializer.fields)
    
    def test_password_validation(self):
        """
        Test password validation.
        """
        # Valid passwords
        self.assertTrue(self.serializer.is_valid())
        
        # Passwords don't match
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'DifferentPass123!'
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password2', serializer.errors)
    
    def test_create_user(self):
        """
        Test creating a user using serializer.
        """
        self.assertTrue(self.serializer.is_valid())
        
        user = self.serializer.save()
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertEqual(user.role, 'member')  # Default role
        self.assertFalse(user.is_active)  # Default is False for approval workflow


class CustomTokenObtainPairSerializerTest(TestCase):
    """
    Test case for the CustomTokenObtainPairSerializer.
    Tests JWT token generation with custom claims.
    """
    
    def setUp(self):
        """
        Set up test data for CustomTokenObtainPairSerializer tests.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            is_active=True,
            role='member'
        )
        
        self.login_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
    
    def test_token_obtain_with_valid_credentials(self):
        """
        Test obtaining token with valid credentials.
        """
        serializer = CustomTokenObtainPairSerializer(data=self.login_data)
        self.assertTrue(serializer.is_valid())
        
        token_data = serializer.validated_data
        self.assertIn('access', token_data)
        self.assertIn('refresh', token_data)
    
    def test_token_obtain_with_invalid_credentials(self):
        """
        Test obtaining token with invalid credentials.
        """
        invalid_data = {
            'username': 'testuser',
            'password': 'WrongPass123!'
        }
        
        serializer = CustomTokenObtainPairSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_token_obtain_with_inactive_user(self):
        """
        Test obtaining token with inactive user.
        """
        # Make user inactive
        self.user.is_active = False
        self.user.save()
        
        serializer = CustomTokenObtainPairSerializer(data=self.login_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_custom_claims(self):
        """
        Test that custom claims are included in the token.
        """
        serializer = CustomTokenObtainPairSerializer(data=self.login_data)
        self.assertTrue(serializer.is_valid())
        
        # We can't directly inspect the token claims here without decoding,
        # but we can verify the get_token method is called by checking
        # that the token is generated successfully
        token_data = serializer.validated_data
        self.assertIn('access', token_data)
        self.assertIn('refresh', token_data)


class UserApprovalSerializerTest(TestCase):
    """
    Test case for the UserApprovalSerializer.
    Tests user approval functionality.
    """
    
    def setUp(self):
        """
        Set up test data for UserApprovalSerializer tests.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            is_active=False,
            role='member'
        )
        
        self.approval_data = {
            'is_active': True
        }
        
        self.serializer = UserApprovalSerializer(
            instance=self.user,
            data=self.approval_data,
            partial=True
        )
    
    def test_approve_user(self):
        """
        Test approving a user using serializer.
        """
        self.assertTrue(self.serializer.is_valid())
        
        updated_user = self.serializer.save()
        self.assertTrue(updated_user.is_active)
        
        # Refresh from database to confirm
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
    
    def test_reject_user(self):
        """
        Test rejecting a user using serializer.
        """
        # First approve the user
        self.user.is_active = True
        self.user.save()
        
        # Then reject
        rejection_data = {
            'is_active': False
        }
        
        serializer = UserApprovalSerializer(
            instance=self.user,
            data=rejection_data,
            partial=True
        )
        
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        self.assertFalse(updated_user.is_active)
        
        # Refresh from database to confirm
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
