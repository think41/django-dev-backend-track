"""
Book models for the Library Management System.

This module defines the Book model for managing book inventory,
including availability tracking and search functionality.
"""

from django.db import models
from django.core.validators import MinValueValidator


class Book(models.Model):
    """
    Book model for library inventory management.
    
    Attributes:
        title: Book title for search and display
        author: Book author for search and display
        genre: Book genre for categorization and search
        total_copies: Total number of copies in the library
        available_copies: Number of copies currently available for borrowing
        created_at: Timestamp when the book was added to the system
    """
    
    title = models.CharField(
        max_length=200,
        help_text="Book title"
    )
    
    author = models.CharField(
        max_length=200,
        help_text="Book author"
    )
    
    genre = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Book genre for categorization"
    )
    
    total_copies = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Total number of copies in the library"
    )
    
    available_copies = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text="Number of copies currently available for borrowing"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the book was added to the system"
    )
    
    class Meta:
        db_table = 'books'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['genre']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def save(self, *args, **kwargs):
        """Override save to ensure available_copies doesn't exceed total_copies."""
        if self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)
    
    @property
    def is_available(self):
        """Check if the book is available for borrowing."""
        return self.available_copies > 0
    
    @property
    def borrowed_copies(self):
        """Get the number of currently borrowed copies."""
        return self.total_copies - self.available_copies
    
    def borrow_copy(self):
        """
        Borrow a copy of the book (decrease available_copies).
        Returns True if successful, False if no copies available.
        """
        if self.available_copies > 0:
            self.available_copies -= 1
            self.save()
            return True
        return False
    
    def return_copy(self):
        """
        Return a copy of the book (increase available_copies).
        Returns True if successful, False if all copies already returned.
        """
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            self.save()
            return True
        return False
    
    def update_copies(self, new_total_copies):
        """
        Update total copies and adjust available copies accordingly.
        Maintains the same number of borrowed copies if possible.
        """
        borrowed = self.borrowed_copies
        self.total_copies = new_total_copies
        self.available_copies = max(0, new_total_copies - borrowed)
        self.save()