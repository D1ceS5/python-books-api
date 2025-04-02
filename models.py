from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from database import Base

book_genre_association = Table(
    "book_genre",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id")),
    Column("genre_id", Integer, ForeignKey("genres.id")),
)

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    birth_date = Column(DateTime, nullable=False)

    books = relationship("Book", back_populates="author")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    isbn = Column(String, nullable=False)
    publish_date = Column(DateTime, nullable=False)

    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="books")

    publisher_id = Column(Integer, ForeignKey("publishers.id"))
    publisher = relationship("Publisher", back_populates="books")

    genres = relationship("Genre", secondary=book_genre_association, back_populates="books")

    borrows = relationship("Borrow", back_populates="book")
    returns = relationship("Return", back_populates="book")


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    books = relationship("Book", secondary=book_genre_association, back_populates="genres")


class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"))
    is_done = Column(Boolean)

    book = relationship("Book", back_populates="borrows")

    created_at = Column(DateTime, server_default=func.now())


class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"))

    book = relationship("Book", back_populates="returns")

    created_at = Column(DateTime, server_default=func.now())

class Publisher(Base):
    __tablename__ = 'publishers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    books = relationship("Book", back_populates='publisher')
