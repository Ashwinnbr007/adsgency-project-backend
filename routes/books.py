from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from pydantic import ValidationError
from models.book import Book
from mongo_connection import books_collection
from utils.utils import object_id_to_string, verify_admin_role

book_bp = Blueprint("books", __name__, url_prefix="/books")


@book_bp.route("/register", methods=["POST"])
def register():
    book_data = request.get_json()
    id = books_collection.count_documents({}) + 1

    unique_book_query = {
        "title": book_data["title"],
        "author": book_data["author"],
        "published_date": book_data["published_date"],
    }

    bookExists = books_collection.find_one(unique_book_query)

    if not bookExists:
        try:
            new_book = Book(bookId=id, **book_data)
        except ValidationError as e:
            return jsonify(message=str(e)), 403

        new_book.published_date = new_book.published_date.strftime("%d-%m-%Y")

        try:
            books_collection.insert_one(dict(new_book))
        except Exception as e:
            return jsonify(message=str(e)), 500

        return jsonify(message="Book registered successfully!"), 201

    return (
        jsonify(message="Book already registered, please register a different book!"),
        409,
    )


@book_bp.route("/display", methods=["GET"])
async def get_all_books():
    try:
        all_books = list(books_collection.find())
        books = []

        for book in all_books:
            book = object_id_to_string(book)
            books.append(book)

        return jsonify(books), 200
    except Exception as e:
        return (
            jsonify(message=f"Server Error!, {str(e)}"),
            500,
        )


@jwt_required()
@book_bp.route("/display/<id_or_title>", methods=["GET"])
async def get_books(id_or_title):
    verify_jwt_in_request()
    if id_or_title.isdigit():
        search = {"bookId": int(id_or_title)}
    else:
        search = {"title": id_or_title}

    try:
        book = books_collection.find_one(search)
        if not book:
            return (
                jsonify(message=f"Book {search} doesnt exist."),
                404,
            )
        book = object_id_to_string(book)
        return jsonify(book), 200
    except Exception as e:
        return (
            jsonify(message=f"Server Error!, {str(e)}"),
            500,
        )


@jwt_required()
@book_bp.route("/filter", methods=["GET"])
async def filter_books():
    verify_jwt_in_request()
    match_query_structure = {
        "genre": "genre",
        "title": "title",
        "author": "author",
        "published_date": "published_date",
        "rating": "review.rating",
    }

    filter_query = {}
    filtered_books = []
    for queries in request.args:
        query = request.args[queries]
        fields = query.split("$")

        if "published_date" in queries:
            query = {"$gte": fields[0]}
            if len(fields) > 1:
                query["$lte"] = fields[1]

        if "rating" in queries:
            query = {"$gte": int(fields[0])}
            if len(fields) > 1:
                query["$lte"] = int(fields[1])

        if queries in match_query_structure:
            filter_query[str(match_query_structure[queries])] = query

    try:
        books = list(books_collection.find(filter_query))
        if not books:
            return (
                jsonify(
                    message=f"There are no books with the filter {filter_query} available."
                ),
                404,
            )
        for book in books:
            book = object_id_to_string(book)
            filtered_books.append(book)
        return jsonify(books), 200
    except Exception as e:
        return (
            jsonify(message=f"Server Error!, {str(e)}"),
            500,
        )


@jwt_required
@book_bp.route("/delete/<bookId>", methods=["DELETE"])
async def delete_books(bookId: int):
    verify_jwt_in_request()
    if not verify_admin_role(get_jwt_identity()):
        return (
            jsonify(message="You are not permitted to perform this action!"),
            401,
        )
    bookExists = books_collection.find_one({"bookId": int(bookId)}) == True
    if not bookExists:
        return (
            jsonify(message="The book does not exist in the collection"),
            404,
        )
    try:
        title_projection = {"title": 1}
        bookTitle = books_collection.find_one(
            {"bookId": int(bookId)}, title_projection
        )["title"]
        books_collection.find_one_and_delete({"bookId": int(bookId)})
        return (
            jsonify(message=f"{bookTitle} deleted"),
            200,
        )
    except Exception as e:
        return (
            jsonify(message=f"Server Error!, {str(e)}"),
            500,
        )
