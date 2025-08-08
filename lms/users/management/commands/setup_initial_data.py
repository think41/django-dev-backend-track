"""
Management command to set up initial data for the Library Management System.

This command creates sample users and books for testing and demonstration purposes.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lms.books.models import Book
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    """Command to set up initial data for LMS."""
    
    help = 'Set up initial data for the Library Management System'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before creating new data',
        )
        parser.add_argument(
            '--users-only',
            action='store_true',
            help='Create only users, not books',
        )
        parser.add_argument(
            '--books-only',
            action='store_true',
            help='Create only books, not users',
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        
        if options['reset']:
            self.stdout.write(
                self.style.WARNING('Resetting all data...')
            )
            User.objects.all().delete()
            Book.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('All data reset successfully')
            )
        
        # Create users unless books-only option is specified
        if not options['books_only']:
            self.create_users()
        
        # Create books unless users-only option is specified
        if not options['users_only']:
            self.create_books()
        
        self.stdout.write(
            self.style.SUCCESS(
                'Initial data setup completed successfully!'
            )
        )
    
    def create_users(self):
        """Create sample users."""
        self.stdout.write('Creating sample users...')
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@library.com',
                'role': 'ADMIN',
                'status': 'ACTIVE',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created admin user: {admin_user.username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Admin user already exists: {admin_user.username}')
            )
        
        # Create sample members
        sample_members = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'status': 'ACTIVE',
                'password': 'john123'
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'status': 'ACTIVE',
                'password': 'jane123'
            },
            {
                'username': 'bob_wilson',
                'email': 'bob@example.com',
                'status': 'PENDING',  # This user is pending approval
                'password': 'bob123'
            },
            {
                'username': 'alice_brown',
                'email': 'alice@example.com',
                'status': 'ACTIVE',
                'password': 'alice123'
            },
            {
                'username': 'mike_johnson',
                'email': 'mike@example.com',
                'status': 'SUSPENDED',  # This user is suspended
                'password': 'mike123'
            }
        ]
        
        for member_data in sample_members:
            user, created = User.objects.get_or_create(
                username=member_data['username'],
                defaults={
                    'email': member_data['email'],
                    'role': 'MEMBER',
                    'status': member_data['status'],
                }
            )
            if created:
                user.set_password(member_data['password'])
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created member: {user.username} (Status: {user.status})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Member already exists: {user.username}'
                    )
                )
        
        # Add some sample borrowing records to active users
        self.add_sample_borrowing_records()
    
    def add_sample_borrowing_records(self):
        """Add sample borrowing records to demonstrate functionality."""
        self.stdout.write('Adding sample borrowing records...')
        
        # Get some active users
        active_users = User.objects.filter(role='MEMBER', status='ACTIVE')[:2]
        
        for i, user in enumerate(active_users):
            # Add some sample borrowing records
            sample_records = [
                {
                    'book_id': i + 1,  # Assuming books will be created
                    'request_date': (datetime.now() - timedelta(days=10)).isoformat(),
                    'approval_date': (datetime.now() - timedelta(days=9)).isoformat(),
                    'due_date': (datetime.now() + timedelta(days=5)).isoformat(),
                    'return_date': None,
                    'status': 'APPROVED'
                },
                {
                    'book_id': i + 3,
                    'request_date': (datetime.now() - timedelta(days=20)).isoformat(),
                    'approval_date': (datetime.now() - timedelta(days=19)).isoformat(),
                    'due_date': (datetime.now() - timedelta(days=5)).isoformat(),
                    'return_date': (datetime.now() - timedelta(days=2)).isoformat(),
                    'status': 'RETURNED'
                },
                {
                    'book_id': i + 5,
                    'request_date': datetime.now().isoformat(),
                    'approval_date': None,
                    'due_date': None,
                    'return_date': None,
                    'status': 'PENDING'
                }
            ]
            
            user.borrowed_books = sample_records
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Added {len(sample_records)} borrowing records for {user.username}'
                )
            )
    
    def create_books(self):
        """Create sample books."""
        self.stdout.write('Creating sample books...')
        
        sample_books = [
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'genre': 'Fiction',
                'total_copies': 3,
                'available_copies': 2  # One copy is borrowed
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'genre': 'Fiction',
                'total_copies': 2,
                'available_copies': 2
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'genre': 'Dystopian Fiction',
                'total_copies': 4,
                'available_copies': 3  # One copy is borrowed
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'genre': 'Romance',
                'total_copies': 2,
                'available_copies': 2
            },
            {
                'title': 'The Catcher in the Rye',
                'author': 'J.D. Salinger',
                'genre': 'Fiction',
                'total_copies': 1,
                'available_copies': 0  # Currently borrowed
            },
            {
                'title': 'Harry Potter and the Philosopher\'s Stone',
                'author': 'J.K. Rowling',
                'genre': 'Fantasy',
                'total_copies': 5,
                'available_copies': 5
            },
            {
                'title': 'The Hobbit',
                'author': 'J.R.R. Tolkien',
                'genre': 'Fantasy',
                'total_copies': 3,
                'available_copies': 3
            },
            {
                'title': 'Dune',
                'author': 'Frank Herbert',
                'genre': 'Science Fiction',
                'total_copies': 2,
                'available_copies': 2
            },
            {
                'title': 'The Hitchhiker\'s Guide to the Galaxy',
                'author': 'Douglas Adams',
                'genre': 'Science Fiction',
                'total_copies': 2,
                'available_copies': 2
            },
            {
                'title': 'Clean Code',
                'author': 'Robert C. Martin',
                'genre': 'Programming',
                'total_copies': 1,
                'available_copies': 1
            }
        ]
        
        for book_data in sample_books:
            book, created = Book.objects.get_or_create(
                title=book_data['title'],
                author=book_data['author'],
                defaults={
                    'genre': book_data['genre'],
                    'total_copies': book_data['total_copies'],
                    'available_copies': book_data['available_copies'],
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created book: "{book.title}" by {book.author} '
                        f'({book.available_copies}/{book.total_copies} available)'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Book already exists: "{book.title}" by {book.author}'
                    )
                )