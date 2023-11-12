from bson import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from pydantic import ValidationError
from custom_exceptions import InvalidIdException
from models.review import Review
from mongo_connection import books_collection, reviews_collection, comments_collection
from utils.utils import create_id, object_id_to_string, verify_admin_role

reviews_bp = Blueprint("reviews", __name__, url_prefix="/reviews")


@jwt_required
@reviews_bp.route("/create", methods=["POST"])
def register():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    reviews_data = request.get_json()

    try:
        book_id = create_id(reviews_data, "bookId")
        user_id = create_id(current_user, "_id")
    except InvalidIdException as invalidId:
        return jsonify(message=str(invalidId)), 403

    bookExists = books_collection.find_one({"_id": book_id})
    if not bookExists:
        return jsonify(message="The book does not exist"), 404

    try:
        del reviews_data["bookId"]
        new_review = Review(userId=str(user_id), **reviews_data)
        new_review_doc = reviews_collection.insert_one(dict(new_review))

        new_review = dict(new_review)
        new_review.update({"_id": new_review_doc.inserted_id})
        books_collection.find_one_and_update(
            {"_id": book_id}, {"$push": {"reviews": new_review}}
        )
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="Review added!"), 201


@jwt_required
@reviews_bp.route("/edit/<review_id>", methods=["PUT"])
def edit_review(review_id):
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    review_data = request.get_json()

    try:
        review_id = create_id(review_id)
        user_id = create_id(current_user, "_id")
    except InvalidIdException as invalidId:
        return jsonify(message=str(invalidId)), 403

    exitsing_review = reviews_collection.find_one({"_id": review_id})

    if not exitsing_review:
        return jsonify(message="Could not find the review!"), 404

    if str(user_id) != exitsing_review["userId"]:
        return jsonify(message="You are not allowed to perform this action!"), 401

    try:
        edit_review = Review(
            userId=str(user_id),
            **review_data,
        )
        reviews_collection.find_one_and_update(
            {"_id": review_id}, {"$set": dict(edit_review)}
        )
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="Review Edited!"), 201


@jwt_required
@reviews_bp.route("/delete/<review_id>", methods=["DELETE"])
def delete_review(review_id):
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    isAdmin = verify_admin_role(current_user)

    try:
        review_id = create_id(review_id)
    except InvalidIdException as invalidId:
        return jsonify(message=str(invalidId)), 403

    exitsing_review = reviews_collection.find_one({"_id": review_id})

    if not exitsing_review:
        return jsonify(message="Could not find the review!"), 404

    if not isAdmin and (exitsing_review["userId"] != current_user["userId"]):
        return jsonify(message="You are not allowed to perform this task!"), 401

    try:
        comment_ids = [
            comment["_id"] for comment in exitsing_review.get("comments", [])
        ]
        comments_collection.delete_many({"_id": {"$in": comment_ids}})
        reviews_collection.delete_one({"_id": review_id})
        books_collection.update_one(
            {"reviews._id": review_id}, {"$pull": {"reviews": {"_id": review_id}}}
        )

    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="Review Deleted!"), 200


@jwt_required
@reviews_bp.route("/retreive", methods=["GET"])
def retreive_review():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    is_admin = verify_admin_role(current_user)

    all_reviews_of_user = object_id_to_string(
        list(reviews_collection.find({"userId": str(current_user["_id"])}))
    )

    try:
        if is_admin:
            all_other_reviews = object_id_to_string(
                list(
                    reviews_collection.find(
                        {"userId": {"$ne": str(current_user["_id"])}}
                    )
                )
            )
            return (
                jsonify(
                    your_reviews=all_reviews_of_user,
                    all_other_reviews=all_other_reviews,
                ),
                200,
            )

        if not all_reviews_of_user:
            return jsonify(message="You do not have any reviews"), 404

        return jsonify(all_reviews_of_user), 200

    except Exception as e:
        return jsonify(message=f"Server error!, {str(e)}"), 500
