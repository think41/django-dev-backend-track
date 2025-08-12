import pytest
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from books.tests.fixtures import UserFixture, BookFixture
from users.tests.fixtures import AuthFixture

User = get_user_model()


class BookAPITest(APITestCase):
    """
    Integration tests for Book API endpoints.
    Tests CRUD operations with proper permissions.
    
    This test suite verifies that:
    1. Books can be listed, retrieved, created, updated, and deleted with proper permissions
    2. Permission checks work correctly for different user roles
    3. Search and ordering functionality works as expected
    """
    
    def setUp(self):
        """
        Set up test data for Book API tests using fixtures.
        """
        # Create users with different roles
        self.admin_user = UserFixture.create_admin_user()
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
            quantity=3
        )
        
        # URLs
        self.book_list_url = reverse('book-list')
        self.book1_detail_url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        self.book2_detail_url = reverse('book-detail', kwargs={'pk': self.book2.pk})
    
    def authenticate_as_admin(self):
        """Helper method to authenticate as admin"""
        AuthFixture.authenticate_client(self.client, self.admin_user)
    
    def authenticate_as_member(self):
        """Helper method to authenticate as member"""
        AuthFixture.authenticate_client(self.client, self.member_user)
    
    def authenticate_as_inactive(self):
        """Helper method to authenticate as inactive user"""
        AuthFixture.authenticate_client(self.client, self.inactive_user)
    
    def clear_authentication(self):
        """Helper method to clear authentication"""
        AuthFixture.clear_authentication(self.client)
    
    def test_list_books_as_admin(self):
        """
        Test listing all books as admin.
        """
        self.authenticate_as_admin()
        response = self.client.get(self.book_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], self.book1.title)
        self.assertEqual(response.data[1]['title'], self.book2.title)
    
    def test_list_books_as_member(self):
        """
        Test listing all books as member.
        """
        self.authenticate_as_member()
        response = self.client.get(self.book_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_list_books_as_inactive(self):
        """
        Test listing all books as inactive user (should be forbidden).
        """
        self.authenticate_as_inactive()
        response = self.client.get(self.book_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_books_unauthenticated(self):
        """
        Test listing all books without authentication (should be unauthorized).
        """
        self.clear_authentication()
        response = self.client.get(self.book_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_book_as_admin(self):
        """
        Test retrieving a specific book as admin.
        """
        self.authenticate_as_admin()
        response = self.client.get(self.book1_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
        self.assertEqual(response.data['author'], self.book1.author)
        self.assertEqual(response.data['isbn'], self.book1.isbn)
    
    def test_retrieve_book_as_member(self):
        """
        Test retrieving a specific book as member.
        """
        self.authenticate_as_member()
        response = self.client.get(self.book1_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
    
    def test_create_book_as_admin(self):
        """
        Test creating a book as admin.
        """
        self.authenticate_as_admin()
        
        new_book_data = {
            'title': 'New Book',
            'author': 'New Author',
            'genre': 'Mystery',
            'isbn': '5555555555555',
            'publication_date': '2023-01-01',
            'cover_image_url': 'http://example.com/new-cover.jpg',
            'quantity': 10
        }
        
        response = self.client.post(self.book_list_url, new_book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        
        new_book = Book.objects.get(title='New Book')
        self.assertEqual(new_book.author, 'New Author')
        self.assertEqual(new_book.quantity, 10)
    
    def test_create_book_as_member(self):
        """
        Test creating a book as member (should be forbidden).
        """
        self.authenticate_as_member()
        
        new_book_data = {
            'title': 'Member Book',
            'author': 'Member Author',
            'genre': 'Fantasy',
            'quantity': 2
        }
        
        response = self.client.post(self.book_list_url, new_book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 2)  # No new book created
    
    def test_update_book_as_admin(self):
        """
        Test updating a book as admin.
        """
        self.authenticate_as_admin()
        
        update_data = {
            'title': 'Updated Book 1',
            'quantity': 8
        }
        
        response = self.client.patch(self.book1_detail_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh book from database
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated Book 1')
        self.assertEqual(self.book1.quantity, 8)
    
    def test_update_book_as_member(self):
        """
        Test updating a book as member (should be forbidden).
        """
        self.authenticate_as_member()
        
        update_data = {
            'title': 'Member Updated Book',
            'quantity': 1
        }
        
        response = self.client.patch(self.book1_detail_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Refresh book from database - should be unchanged
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Test Book 1')
        self.assertEqual(self.book1.quantity, 5)
    
    def test_delete_book_as_admin(self):
        """
        Test deleting a book as admin.
        """
        self.authenticate_as_admin()
        
        response = self.client.delete(self.book1_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 1)
        self.assertFalse(Book.objects.filter(pk=self.book1.pk).exists())
    
    def test_delete_book_as_member(self):
        """
        Test deleting a book as member (should be forbidden).
        """
        self.authenticate_as_member()
        
        response = self.client.delete(self.book1_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 2)
        self.assertTrue(Book.objects.filter(pk=self.book1.pk).exists())
    
    def test_search_books(self):
        """
        Test searching books by title, author, genre, and ISBN.
        """
        self.authenticate_as_member()
        
        # Search by title
        response = self.client.get(f"{self.book_list_url}?search=Book 1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Book 1')
        
        # Search by author
        response = self.client.get(f"{self.book_list_url}?search=Author 2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Book 2')
        
        # Search by genre
        response = self.client.get(f"{self.book_list_url}?search=Fiction")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Book 1')
        
        # Search by ISBN
        response = self.client.get(f"{self.book_list_url}?search=9876543210987")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Book 2')
    
    def test_ordering_books(self):
        """
        Test ordering books by different fields.
        """
        self.authenticate_as_member()
        
        # Order by title ascending (default)
        response = self.client.get(f"{self.book_list_url}?ordering=title")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'Test Book 1')
        self.assertEqual(response.data[1]['title'], 'Test Book 2')
        
        # Order by title descending
        response = self.client.get(f"{self.book_list_url}?ordering=-title")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'Test Book 2')
        self.assertEqual(response.data[1]['title'], 'Test Book 1')
        
        # Order by author
        response = self.client.get(f"{self.book_list_url}?ordering=author")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['author'], 'Test Author 1')
        self.assertEqual(response.data[1]['author'], 'Test Author 2')
