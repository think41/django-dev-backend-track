from ..data import BookRepository
from ..models import Book


class BookService:
    @staticmethod
    def add_book(**data) -> Book:
        return BookRepository.create(**data)

    @staticmethod
    def update_book(book: Book, **data) -> Book:
        return BookRepository.update(book, **data)

    @staticmethod
    def delete_book(book: Book):
        BookRepository.delete(book)
