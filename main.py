from fastapi import FastAPI
from database import engine, Base
from routes import book,author,publisher,genre, borrow

DEFAULT_PREFIX = "/api"

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library API")

app.include_router(book.router, prefix=DEFAULT_PREFIX, tags=["Books"])
app.include_router(author.router, prefix=DEFAULT_PREFIX, tags=['Authors'])
app.include_router(publisher.router, prefix=DEFAULT_PREFIX, tags=['Publishers'])
app.include_router(genre.router, prefix=DEFAULT_PREFIX, tags=['Genre'])
app.include_router(borrow.router, prefix=DEFAULT_PREFIX, tags=['Borrow'])
