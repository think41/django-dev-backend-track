from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    Adds role field and modifies is_active default to False for approval workflow.
    """
    ROLE_CHOICES = (
        ('admin', _('Admin')),
        ('member', _('Member')),
    )
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(_('role'), max_length=10, choices=ROLE_CHOICES, default='member')
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.username
