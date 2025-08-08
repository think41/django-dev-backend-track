from typing import Optional
from django.db.models import Q
from ..models import Book


class BookRepository:
    @staticmethod
    def create(**kwargs) -> Book:
        return Book.objects.create(**kwargs)

    @staticmethod
    def update(book: Book, **kwargs) -> Book:
        for k, v in kwargs.items():
            setattr(book, k, v)
        book.save()
        return book

    @staticmethod
    def delete(book: Book):
        book.delete()

    @staticmethod
    def get_by_id(book_id) -> Optional[Book]:
        try:
            return Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return None

    @staticmethod
    def search(query: str):
        return Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query) | Q(genre__icontains=query)
        ).order_by("title")

    @staticmethod
    def list_all():
        return Book.objects.all().order_by("title")
