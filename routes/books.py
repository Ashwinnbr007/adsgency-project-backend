from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from models.book import CreateBook, Book
from mongo_connection import books_collection

book_bp = Blueprint("books", __name__, url_prefix="/books")


@book_bp.route("/register", methods=["POST"])
def register():
    book_data = request.get_json()
    try:
        data = CreateBook(**book_data)
    except ValidationError as e:
        return jsonify(message=str(e)), 400

    id = books_collection.count_documents({}) + 1
    bookExists = books_collection.find_one({"title": data.title, "author": data.author})
    
    if not bookExists:
        new_book = Book(bookId=id,**book_data)
        new_book.published_date = new_book.published_date.strftime("%d-%m-%Y")
        new_book.review = dict(new_book.review)
        try:
            books_collection.insert_one(dict(new_book))
        except Exception as e:
            return jsonify(message=str(e)), 500

        return jsonify(message="Book registered successfully!"), 201
    
    return jsonify(message="Book already registered, please register a different book!"), 409


# @book_bp.route("/register", methods=["POST"])
# def register():
#     book_data = request.get_json()
#     try:
#         data = CreateBook(**book_data)
#     except ValidationError as e:
#         return jsonify(message=str(e)), 400

#     id = books_collection.count_documents({}) + 1
#     bookExists = books_collection.find_one({"title": data.title, "author": data.author})
    
#     if not bookExists:
#         new_book = Book(bookId=id,**book_data)
#         new_book.published_date = new_book.published_date.strftime("%d-%m-%Y")
#         try:
#             books_collection.insert_one(dict(new_book))
#         except Exception as e:
#             return jsonify(message=str(e)), 500

#         return jsonify(message="Book registered successfully!"), 201
    
#     return jsonify(message="Book already registered, please register a different book!"), 409
