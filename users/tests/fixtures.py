"""
Test fixtures for users app.

This module provides reusable fixtures for setting up test data
for users with different roles and authentication states.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserFixture:
    """
    Fixture for creating test users with different roles.
    """
    
    @staticmethod
    def create_admin_user(username='admin', email='admin@example.com', 
                         password='AdminPass123!', is_active=True):
        """Create an admin user for testing."""
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=is_active,
            role='admin',
            is_staff=True
        )
    
    @staticmethod
    def create_librarian_user(username='librarian', email='librarian@example.com', 
                             password='LibrarianPass123!', is_active=True):
        """Create a librarian user for testing."""
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=is_active,
            role='librarian'
        )
    
    @staticmethod
    def create_member_user(username='member', email='member@example.com', 
                          password='MemberPass123!', is_active=True):
        """Create a member user for testing."""
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=is_active,
            role='member'
        )
    
    @staticmethod
    def create_inactive_user(username='inactive', email='inactive@example.com', 
                            password='InactivePass123!'):
        """Create an inactive user for testing."""
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False,
            role='member'
        )
    
    @staticmethod
    def create_superuser(username='superadmin', email='superadmin@example.com', 
                        password='SuperAdminPass123!'):
        """Create a superuser for testing."""
        return User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )


class AuthFixture:
    """
    Fixture for authentication-related test helpers.
    """
    
    @staticmethod
    def get_tokens_for_user(user):
        """Get JWT tokens for a user."""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    @staticmethod
    def authenticate_client(client, user):
        """Authenticate a test client with a user's JWT token."""
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client
    
    @staticmethod
    def clear_authentication(client):
        """Clear authentication credentials from a test client."""
        client.credentials()
        return client


class RegistrationFixture:
    """
    Fixture for user registration test data.
    """
    
    @staticmethod
    def get_valid_registration_data(username='newuser', email='newuser@example.com', 
                                  password='NewPass123!'):
        """Get valid user registration data."""
        return {
            'username': username,
            'email': email,
            'password': password,
            'password2': password
        }
    
    @staticmethod
    def get_invalid_registration_data():
        """Get various invalid registration data scenarios."""
        return {
            'mismatched_passwords': {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'NewPass123!',
                'password2': 'DifferentPass123!'
            },
            'short_password': {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'short',
                'password2': 'short'
            },
            'missing_username': {
                'username': '',
                'email': 'newuser@example.com',
                'password': 'NewPass123!',
                'password2': 'NewPass123!'
            },
            'missing_email': {
                'username': 'newuser',
                'email': '',
                'password': 'NewPass123!',
                'password2': 'NewPass123!'
            }
        }
