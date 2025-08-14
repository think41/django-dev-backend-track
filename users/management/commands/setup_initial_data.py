from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from books.models import Book

User = get_user_model()


class Command(BaseCommand):
    help = 'Create initial admin user and sample data'

    def handle(self, *args, **options):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@library.com',
                password='admin123',
                role='admin',
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Admin user created: {admin_user.username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )

        # Create sample member user
        if not User.objects.filter(username='member1').exists():
            member_user = User.objects.create_user(
                username='member1',
                email='member1@library.com',
                password='member123',
                role='member',
                is_active=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Member user created: {member_user.username}')
            )

        # Create sample books
        sample_books = [
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'genre': 'Fiction',
                'quantity': 3
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'genre': 'Dystopian Fiction',
                'quantity': 2
            },
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'genre': 'Classic Literature',
                'quantity': 4
            },
            {
                'title': 'Python Crash Course',
                'author': 'Eric Matthes',
                'genre': 'Programming',
                'quantity': 5
            },
            {
                'title': 'Clean Code',
                'author': 'Robert C. Martin',
                'genre': 'Programming',
                'quantity': 2
            }
        ]

        for book_data in sample_books:
            if not Book.objects.filter(title=book_data['title']).exists():
                book = Book.objects.create(**book_data)
                self.stdout.write(
                    self.style.SUCCESS(f'Book created: {book.title}')
                )

        self.stdout.write(
            self.style.SUCCESS('Initial data setup completed!')
        ) 