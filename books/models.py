from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Book(models.Model):
    """
    Represents a single book title in the library's collection.
    """
    title = models.CharField(_('title'), max_length=255)
    author = models.CharField(_('author'), max_length=255)
    genre = models.CharField(_('genre'), max_length=100)
    quantity = models.PositiveIntegerField(_('quantity'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('book')
        verbose_name_plural = _('books')
        ordering = ['title', 'author']
    
    def __str__(self):
        return f"{self.title} by {self.author}"


class BorrowRecord(models.Model):
    """
    Tracks the status and history of a single borrowing transaction.
    """
    STATUS_CHOICES = (
        ('PENDING', _('Pending')),
        ('APPROVED', _('Approved')),
        ('REJECTED', _('Rejected')),
        ('RETURNED', _('Returned')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='borrow_records',
        verbose_name=_('user')
    )
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        related_name='borrow_records',
        verbose_name=_('book')
    )
    borrow_date = models.DateField(_('borrow date'), null=True, blank=True)
    return_date = models.DateField(_('return date'), null=True, blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('borrow record')
        verbose_name_plural = _('borrow records')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.status}"
