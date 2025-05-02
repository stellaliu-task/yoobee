# definded a class of book
class Book:
    #an unique ID to each book
    next_id = 10001
    # created a book object and do some initial works
    def __init__(self, subject, title, author):
        self.id = Book.next_id
        Book.next_id += 1
        self.subject = subject
        self.title = title
        self.author = author

    def display(self):
        print(f" Id: {self.id}")
        print(f"Subject:{self.subject}")
        print(f"Title:{self.title}")
        print(f"Author:{self.author}")
        print("-" * 30)

# definded a class of library
class Library:
    def __init__(self):
        self.books = []

    def add_book(self, subject, title, author):
        new_book = Book(subject, title, author)
        self.books.append(new_book)
        print('New book added'); print(f" Id: {new_book.id} Title: {new_book.title}")
        print("-" * 30)

    def show_book(self):
        if not self.books:
            print('No book in the library')
        else:   
            print('There are books in the library:')
            print("*" * 30)
            for book in self.books:
                book.display()


def main():
    library = Library()
    library.add_book('Fiction', 'Onyx storm', 'Rebecca Yarros')
    library.add_book('Mystery', 'The life we bury', 'Allen Eskens')
    library.show_book()
    
if __name__ == "__main__":
    main()