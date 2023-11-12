from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from pydantic import ValidationError
from models.review import Review
from mongo_connection import comments_collection, books_collection, reviews_collection
from utils.utils import object_id_to_string, verify_admin_role

reviews_bp = Blueprint("reviews", __name__, url_prefix="/reviews")


@jwt_required
@reviews_bp.route("/create", methods=["POST"])
def register():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    reviews_data = request.get_json()
    id = reviews_collection.count_documents({}) + 1

    bookExists = books_collection.find_one({"bookId": reviews_data["bookId"]})
    if not bookExists:
        return jsonify(message="The book does not exist"), 404

    try:
        new_review = Review(reviewId=id, userId=current_user["userId"], **reviews_data)
        reviews_collection.insert_one(dict(new_review))
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="Review added!"), 201


@jwt_required
@reviews_bp.route("/edit/<review_id>", methods=["PUT"])
def edit_review(review_id: int):
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    review_data = request.get_json()

    exitsing_review = reviews_collection.find_one({"reviewId": int(review_id)})

    if not exitsing_review:
        return jsonify(message="Could not find the review!"), 404

    if current_user["userId"] != exitsing_review["userId"]:
        return jsonify(message="You are not allowed to perform this action!"), 401

    try:
        edit_review = Review(
            userId=current_user["userId"],
            bookId=exitsing_review["bookId"],
            reviewId=int(review_id),
            **review_data,
        )
        reviews_collection.find_one_and_update(
            {"reviewId": int(review_id)}, {"$set": dict(edit_review)}
        )
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="Review Edited!"), 201


@jwt_required
@reviews_bp.route("/delete/<review_id>", methods=["DELETE"])
def delete_review(review_id: int):
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    isAdmin = verify_admin_role(current_user)

    exitsing_review = reviews_collection.find_one({"reviewId": int(review_id)})

    if not exitsing_review:
        return jsonify(message="Could not find the review!"), 404

    if not isAdmin and (exitsing_review["userId"] != current_user["userId"]):
        return jsonify(message="You are not allowed to perform this task!"), 401

    try:
        reviews_collection.find_one_and_delete({"reviewId": int(review_id)})
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="Review Deleted!"), 201


@jwt_required
@reviews_bp.route("/retreive", methods=["GET"])
def retreive_review():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    is_admin = verify_admin_role(current_user)

    all_reviews_of_user = object_id_to_string(
        list(reviews_collection.find({"userId": int(current_user["userId"])}))
    )

    try:
        if is_admin:
            all_other_reviews = object_id_to_string(
                list(
                    reviews_collection.find(
                        {"userId": {"$ne": int(current_user["userId"])}}
                    )
                )
            )
            return (
                jsonify(your_reviews=all_reviews_of_user, all_other_reviews=all_other_reviews),
                200,
            )

        if not all_reviews_of_user:
            return jsonify(message="You do not have any reviews"), 404

        return jsonify(all_reviews_of_user), 200

    except Exception as e:
        return jsonify(message=f"Server error!, {str(e)}"), 500
