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
    isbn = models.CharField(_('ISBN'), max_length=13, blank=True, null=True)
    publication_date = models.DateField(_('publication date'), blank=True, null=True)
    cover_image_url = models.URLField(_('cover image URL'), blank=True, null=True)
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
    due_date = models.DateField(_('due date'), null=True, blank=True)
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


class Reservation(models.Model):
    """
    Represents a member's reservation for a book that is currently unavailable.
    """
    STATUS_CHOICES = (
        ('PENDING', _('Pending')),
        ('FULFILLED', _('Fulfilled')),
        ('CANCELLED', _('Cancelled')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name=_('user')
    )
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name=_('book')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    reservation_date = models.DateTimeField(_('reservation date'), auto_now_add=True)
    notification_sent = models.BooleanField(_('notification sent'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('reservation')
        verbose_name_plural = _('reservations')
        ordering = ['-reservation_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.status}"


class Fine(models.Model):
    """
    Tracks fines imposed on members for overdue books.
    """
    STATUS_CHOICES = (
        ('PENDING', _('Pending')),
        ('PAID', _('Paid')),
        ('WAIVED', _('Waived')),
    )
    
    borrow_record = models.ForeignKey(
        'BorrowRecord',
        on_delete=models.CASCADE,
        related_name='fines',
        verbose_name=_('borrow record')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fines',
        verbose_name=_('user')
    )
    amount = models.DecimalField(_('amount'), max_digits=6, decimal_places=2)
    reason = models.CharField(_('reason'), max_length=255)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    days_overdue = models.PositiveIntegerField(_('days overdue'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('fine')
        verbose_name_plural = _('fines')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.borrow_record.book.title} - {self.amount}"
