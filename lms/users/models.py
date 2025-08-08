"""
User models for the Library Management System.

This module defines the custom User model that extends Django's AbstractUser
to add library-specific functionality like roles, status, and borrowing records.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    Attributes:
        email: Unique email field for the user
        role: User role (ADMIN or MEMBER)
        status: Account status (PENDING, ACTIVE, SUSPENDED)
        borrowed_books: JSON field storing array of borrowing records
    """
    
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    # Override email to make it unique and required
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Required. Enter a valid email address."
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='MEMBER',
        help_text="User role in the system"
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Account approval status"
    )
    
    borrowed_books = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of borrowing records with metadata"
    )
    
    # Make email the username field for authentication
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def save(self, *args, **kwargs):
        """Override save to set is_staff for admin users."""
        if self.role == 'ADMIN':
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)
    
    @property
    def is_active_member(self):
        """Check if user is an active member who can borrow books."""
        return self.status == 'ACTIVE' and self.role == 'MEMBER'
    
    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'ADMIN'
    
    def get_active_borrowings(self):
        """Get all currently borrowed (not returned) books."""
        return [
            record for record in self.borrowed_books
            if record.get('status') == 'APPROVED' and not record.get('return_date')
        ]
    
    def get_borrowing_history(self):
        """Get complete borrowing history."""
        return self.borrowed_books
    
    def add_borrow_request(self, book_id):
        """Add a new borrow request to the user's records."""
        from datetime import datetime
        
        borrow_record = {
            'book_id': book_id,
            'request_date': datetime.now().isoformat(),
            'approval_date': None,
            'due_date': None,
            'return_date': None,
            'status': 'PENDING'
        }
        
        self.borrowed_books.append(borrow_record)
        self.save()
        return borrow_record
    
    def update_borrow_status(self, book_id, status, approval_date=None, due_date=None):
        """Update the status of a borrow request."""
        for record in self.borrowed_books:
            if record['book_id'] == book_id and record['status'] == 'PENDING':
                record['status'] = status
                if approval_date:
                    record['approval_date'] = approval_date.isoformat()
                if due_date:
                    record['due_date'] = due_date.isoformat()
                break
        self.save()
    
    def return_book(self, book_id):
        """Mark a book as returned."""
        from datetime import datetime
        
        for record in self.borrowed_books:
            if (record['book_id'] == book_id and 
                record['status'] == 'APPROVED' and 
                not record.get('return_date')):
                record['return_date'] = datetime.now().isoformat()
                record['status'] = 'RETURNED'
                break
        self.save()