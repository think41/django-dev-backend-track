import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.books.models import Book
from app.users.models import BookRequest

User = get_user_model()

class Command(BaseCommand):
    help = "Load sample users and borrow records from CSV"

    def handle(self, *args, **kwargs):
        # Load users
        with open('data/users.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user, created = User.objects.get_or_create(
                    email=row['email'],
                    defaults={
                        'username': row['username'],
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'role': row['role'],
                        'is_approved': row['is_approved'].lower() == 'true',
                    }
                )
                if created:
                    user.set_password(row['password'])
                    user.save()

        with open("data/books.csv") as f:
            for row in csv.DictReader(f):
                Book.objects.create(
                    title=row["title"],
                    author=row["author"],
                    genre=row["genre"],
                    publication_year=int(row["publication_year"]),
                    available_copies=int(row["available_copies"]),
                    summary=row["summary"]
                )


        self.stdout.write(self.style.SUCCESS("Data loaded successfully"))
