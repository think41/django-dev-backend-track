import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.books.models import Book, BorrowRecord

BASE_DIR = Path(__file__).resolve().parents[4]
DATA_DIR = BASE_DIR / 'data'


class Command(BaseCommand):
    help = 'Seed initial users, books, and borrow records from CSV files in data/'

    def handle(self, *args, **options):
        User = get_user_model()
        # Ensure a default admin exists and has correct privileges
        admin = User.objects.filter(username='admin').first()
        if not admin:
            try:
                # Prefer the manager's superuser creator
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin',
                )
            except Exception:
                # Fallback if custom manager signature differs
                admin = User.objects.create_user(
                    username='admin',
                    email='admin@example.com',
                    password='admin',
                    role='ADMIN',
                    is_active=True,
                )
                # Elevate privileges explicitly
                setattr(admin, 'is_staff', True)
                setattr(admin, 'is_superuser', True)
                admin.save(update_fields=['is_staff', 'is_superuser'])
            self.stdout.write(self.style.SUCCESS("Created user admin"))
        else:
            changed = False
            if getattr(admin, 'role', None) != 'ADMIN':
                setattr(admin, 'role', 'ADMIN')
                changed = True
            if not getattr(admin, 'is_active', True):
                setattr(admin, 'is_active', True)
                changed = True
            if not getattr(admin, 'is_staff', False):
                setattr(admin, 'is_staff', True)
                changed = True
            if not getattr(admin, 'is_superuser', False):
                setattr(admin, 'is_superuser', True)
                changed = True
            # Reset password to known default to avoid login issues
            admin.set_password('admin')
            changed = True
            if changed:
                admin.save()
                self.stdout.write(self.style.WARNING("Updated existing 'admin' user privileges/password"))

        # Users
        users_csv = DATA_DIR / 'users.csv'
        if users_csv.exists():
            with users_csv.open() as f:
                reader = csv.DictReader(f)
                for row in reader:
                    username = row['username']
                    email = row['email']
                    role = row['role'].upper()
                    is_approved = row['is_approved'].strip().lower() == 'true'
                    if not User.objects.filter(username=username).exists():
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=row['password'],
                            first_name=row.get('first_name') or '',
                            last_name=row.get('last_name') or '',
                            role='ADMIN' if role == 'ADMIN' else 'MEMBER',
                            is_active=is_approved,
                        )
                        self.stdout.write(self.style.SUCCESS(f"Created user {username}"))

        # Books
        books_csv = DATA_DIR / 'books.csv'
        if books_csv.exists():
            with books_csv.open() as f:
                reader = csv.DictReader(f)
                for row in reader:
                    title = row['title']
                    author = row['author']
                    genre = row.get('genre') or ''
                    isbn = row.get('isbn', '').strip()
                    publication_date = (row.get('publication_date') or '').strip()
                    cover_image_url = (row.get('cover_image_url') or '').strip()
                    available_copies = int(row.get('available_copies') or 0)
                    if not Book.objects.filter(title=title, author=author).exists():
                        create_kwargs = dict(
                            title=title,
                            author=author,
                            genre=genre,
                            isbn=isbn,
                            cover_image_url=cover_image_url,
                            available_copies=available_copies,
                        )
                        # parse date if provided (YYYY-MM-DD)
                        if publication_date:
                            try:
                                create_kwargs['publication_date'] = publication_date
                            except Exception:
                                pass
                        Book.objects.create(**create_kwargs)
                        self.stdout.write(self.style.SUCCESS(f"Created book {title}"))

        # Borrow Records (optional, uses usernames and titles for mapping simplicity)
        # Skipping because CSV has numeric IDs that don't match UUIDs; could be extended later.
        self.stdout.write(self.style.SUCCESS('Seeding completed.'))
