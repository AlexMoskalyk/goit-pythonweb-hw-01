import logging
from abc import ABC, abstractmethod
from typing import List

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SRP: Відокремлений клас Book для представлення книги
class Book:
    def __init__(self, title: str, author: str, year: str):
        self.title = title
        self.author = author
        self.year = year

    def __str__(self) -> str:
        return f"Title: {self.title}, Author: {self.author}, Year: {self.year}"

# ISP: Визначаємо чіткий інтерфейс для бібліотеки
class LibraryInterface(ABC):
    @abstractmethod
    def add_book(self, book: Book) -> None:
        pass

    @abstractmethod
    def remove_book(self, title: str) -> None:
        pass

    @abstractmethod
    def get_books(self) -> List[Book]:
        pass

# OCP, LSP: Клас Library реалізує інтерфейс LibraryInterface, підтримуючи розширюваність
class Library(LibraryInterface):
    def __init__(self) -> None:
        self._books: List[Book] = []

    def add_book(self, book: Book) -> None:
        self._books.append(book)
        logger.info(f"Book added: {book}")

    def remove_book(self, title: str) -> None:
        self._books = [book for book in self._books if book.title != title]
        logger.info(f"Book removed: {title}")

    def get_books(self) -> List[Book]:
        return self._books

# DIP: Клас LibraryManager працює через абстракцію LibraryInterface
class LibraryManager:
    def __init__(self, library: LibraryInterface) -> None:
        self.library = library

    def add_book(self, title: str, author: str, year: str) -> None:
        book = Book(title, author, year)
        self.library.add_book(book)

    def remove_book(self, title: str) -> None:
        self.library.remove_book(title)

    def show_books(self) -> None:
        books = self.library.get_books()
        if books:
            for book in books:
                logger.info(book)
        else:
            logger.info("No books in the library.")

# Функція main для запуску програми
def main() -> None:
    library = Library()
    manager = LibraryManager(library)

    while True:
        command = input("Enter command (add, remove, show, exit): ").strip().lower()

        match command:
            case "add":
                title = input("Enter book title: ").strip()
                author = input("Enter book author: ").strip()
                year = input("Enter book year: ").strip()
                manager.add_book(title, author, year)
            case "remove":
                title = input("Enter book title to remove: ").strip()
                manager.remove_book(title)
            case "show":
                manager.show_books()
            case "exit":
                break
            case _:
                logger.warning("Invalid command. Please try again.")

if __name__ == "__main__":
    main()
