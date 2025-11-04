from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import pandas as pd
from typing import Optional
from fastapi.responses import JSONResponse

app = FastAPI()

API_KEY = "cennext"

def verify_api_key(authorization: Optional[str] = Header(None)):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Xác thực thất bại, nhập lại key.")

books_df = pd.read_csv('books_with_country.csv')

class Book(BaseModel):
    title: str
    price: str
    availability: str
    page_link: str
    rating: Optional[int]
    publisher_country: str

@app.get("/books")
def get_books(authorization: str = Depends(verify_api_key)):
    books = books_df.to_dict(orient='records')
    return JSONResponse(content=books)

@app.get("/books/country")
def get_books_by_country(country: str, authorization: str = Depends(verify_api_key)):
    books_in_country = books_df[books_df['publisher_country'] == country]
    if books_in_country.empty:
        raise HTTPException(status_code=404, detail=f"Không có sách nào được xuất bản ở {country}")
    return JSONResponse(content=books_in_country.to_dict(orient='records'))

@app.post("/books")
def add_book(book: Book, authorization: str = Depends(verify_api_key)):
    new_book = {
        "title": book.title,
        "price": book.price,
        "availability": book.availability,
        "page_link": book.page_link,
        "rating": book.rating,
        "publisher_country": book.publisher_country,
    }
    books_df.loc[len(books_df)] = new_book
    books_df.to_csv('books_with_country.csv', index=False)
    return new_book

@app.delete("/books/{title}")
def delete_book(title: str, authorization: str = Depends(verify_api_key)):
    global books_df
    book_to_delete = books_df[books_df['title'] == title]
    if book_to_delete.empty:
        raise HTTPException(status_code=404, detail="Sách này không tồn tại.")
    
    books_df = books_df[books_df['title'] != title] 
    books_df.to_csv('books_with_country.csv', index=False)
    return {"message": f"Sách '{title}' đã được xóa."}

@app.get("/")
def main():
    return {"message": "Cennext - Phạm Thanh Hải"}
