import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from books.models import Book, BorrowRecord
from datetime import datetime

User = get_user_model()


class Command(BaseCommand):
    help = 'Load data from CSV files and replace existing data'

    def handle(self, *args, **options):
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        BorrowRecord.objects.all().delete()
        Book.objects.all().delete()
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Existing data cleared'))

        # Load users
        self.load_users()
        # Load books
        self.load_books()
        # Load borrow records
        self.load_borrow_records()

        self.stdout.write(self.style.SUCCESS('Data loading completed!'))

    def load_users(self):
        users_csv_path = 'data/users.csv'
        if not os.path.exists(users_csv_path):
            self.stdout.write(self.style.ERROR(f'File not found: {users_csv_path}'))
            return

        with open(users_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row['username']:  # Skip empty rows
                    continue
                
                user = User.objects.create_user(
                    username=row['username'],
                    password=row['password'],
                    email=row['email'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    role=row['role'].lower(),
                    is_active=row['is_approved'].lower() == 'true'
                )
                
                # Set admin privileges for admin users
                if user.role == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'User created: {user.username} ({user.role})')
                )

    def load_books(self):
        books_csv_path = 'data/books.csv'
        if not os.path.exists(books_csv_path):
            self.stdout.write(self.style.ERROR(f'File not found: {books_csv_path}'))
            return

        with open(books_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row['title']:  # Skip empty rows
                    continue
                
                book = Book.objects.create(
                    title=row['title'],
                    author=row['author'],
                    genre=row['genre'],
                    quantity=int(row['available_copies'])
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Book created: {book.title} by {book.author}')
                )

    def load_borrow_records(self):
        # Create sample borrow records based on the CSV data pattern
        # Using usernames and book titles instead of IDs
        try:
            member1 = User.objects.get(username='member1')
            
            # Get books
            hitchhiker = Book.objects.get(title="The Hitchhiker's Guide to the Galaxy")
            mockingbird = Book.objects.get(title="To Kill a Mockingbird")
            
            # Create approved borrow record
            approved_record = BorrowRecord.objects.create(
                user=member1,
                book=hitchhiker,
                borrow_date=datetime.strptime('2025-07-01', '%Y-%m-%d').date(),
                status='APPROVED'
            )
            
            # Adjust book quantity for approved record
            hitchhiker.quantity -= 1
            hitchhiker.save()
            
            # Create pending borrow record
            pending_record = BorrowRecord.objects.create(
                user=member1,
                book=mockingbird,
                status='PENDING'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Borrow record created: {member1.username} - {hitchhiker.title} (APPROVED)')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Borrow record created: {member1.username} - {mockingbird.title} (PENDING)')
            )
            
        except (User.DoesNotExist, Book.DoesNotExist) as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating borrow records: {e}')
            ) 