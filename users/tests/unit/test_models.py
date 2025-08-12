import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class CustomUserManagerTest(TestCase):
    """
    Test case for the CustomUserManager.
    Tests user creation methods and validation.
    """
    
    def test_create_user(self):
        """
        Test creating a regular user with the manager.
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_active)  # Default is False for approval workflow
        self.assertEqual(user.role, 'member')  # Default role
    
    def test_create_user_without_username(self):
        """
        Test creating a user without a username raises error.
        """
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username='',
                email='test@example.com',
                password='TestPass123!'
            )
    
    def test_create_user_without_email(self):
        """
        Test creating a user without an email raises error.
        """
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username='testuser',
                email='',
                password='TestPass123!'
            )
    
    def test_create_superuser(self):
        """
        Test creating a superuser with the manager.
        """
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )
        
        self.assertEqual(admin_user.username, 'admin')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.check_password('AdminPass123!'))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)  # Superusers are active by default
        self.assertEqual(admin_user.role, 'admin')  # Should be admin role
    
    def test_create_superuser_not_staff(self):
        """
        Test creating a superuser with is_staff=False raises error.
        """
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='AdminPass123!',
                is_staff=False
            )
    
    def test_create_superuser_not_superuser(self):
        """
        Test creating a superuser with is_superuser=False raises error.
        """
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='AdminPass123!',
                is_superuser=False
            )


class UserModelTest(TestCase):
    """
    Test case for the User model.
    Tests field validations, methods, and properties.
    """
    
    def setUp(self):
        """
        Set up test data for User model tests.
        """
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'role': 'member'
        }
        
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_creation(self):
        """
        Test basic user creation and field values.
        """
        self.assertEqual(self.user.username, self.user_data['username'])
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertEqual(self.user.role, self.user_data['role'])
        self.assertFalse(self.user.is_active)
    
    def test_user_str_representation(self):
        """
        Test the string representation of a user.
        """
        self.assertEqual(str(self.user), self.user_data['username'])
    
    def test_email_uniqueness(self):
        """
        Test that email addresses must be unique.
        """
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='anotheruser',
                email='test@example.com',  # Same email as existing user
                password='AnotherPass123!'
            )
    
    def test_username_uniqueness(self):
        """
        Test that usernames must be unique.
        """
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='testuser',  # Same username as existing user
                email='another@example.com',
                password='AnotherPass123!'
            )
    
    def test_user_role_choices(self):
        """
        Test that user roles are limited to valid choices.
        """
        # Test valid roles
        self.user.role = 'member'
        self.user.save()
        self.assertEqual(self.user.role, 'member')
        
        self.user.role = 'admin'
        self.user.save()
        self.assertEqual(self.user.role, 'admin')
        
        self.user.role = 'librarian'
        self.user.save()
        self.assertEqual(self.user.role, 'librarian')
    
    def test_user_approval(self):
        """
        Test user approval workflow.
        """
        self.assertFalse(self.user.is_active)  # Initially inactive
        
        # Approve user
        self.user.is_active = True
        self.user.save()
        
        # Refresh from database
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
    
    def test_user_permissions(self):
        """
        Test user permissions based on role.
        """
        # Regular member
        self.user.role = 'member'
        self.assertFalse(self.user.is_staff)
        
        # Librarian
        self.user.role = 'librarian'
        self.user.save()
        self.assertFalse(self.user.is_staff)  # Librarians are not staff by default
        
        # Admin
        self.user.role = 'admin'
        self.user.is_staff = True
        self.user.save()
        self.assertTrue(self.user.is_staff)
