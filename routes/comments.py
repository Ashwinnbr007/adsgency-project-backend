from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from pydantic import ValidationError
from custom_exceptions import InvalidIdException
from models.comment import Comment
from mongo_connection import comments_collection, books_collection
from utils.utils import create_id, object_id_to_string, verify_admin_role

comment_bp = Blueprint("comments", __name__, url_prefix="/comments")


@jwt_required
@comment_bp.route("/create", methods=["POST"])
def register():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    comment_data = request.get_json()
    try:
        book_id = create_id(comment_data, "bookId")
        user_id = create_id(current_user, "_id")
    except InvalidIdException as invalidId:
        return jsonify(message=str(invalidId)), 403

    bookExists = books_collection.find_one({"_id": book_id})
    if not bookExists:
        return jsonify(message="The book does not exist"), 404

    try:
        new_comment = Comment(userId=str(user_id), **comment_data)
        comments_collection.insert_one(dict(new_comment))
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="Comment added!"), 201


@jwt_required
@comment_bp.route("/edit/<comment_id>", methods=["PUT"])
def edit_comment(comment_id):
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    comment_data = request.get_json()

    try:
        comment_id = create_id(comment_id)
        user_id = create_id(current_user, "_id")
    except InvalidIdException as invalidId:
        return jsonify(message=str(invalidId)), 403

    exitsing_comment = comments_collection.find_one({"_id": comment_id})

    if not exitsing_comment:
        return jsonify(message="Could not find the comment!"), 404

    if str(user_id) != exitsing_comment["userId"]:
        return jsonify(message="You are not allowed to perform this action!"), 401

    try:
        edit_comment = Comment(
            userId=str(user_id),
            bookId=exitsing_comment["bookId"],
            **comment_data,
        )
        comments_collection.find_one_and_update(
            {"_id": comment_id}, {"$set": dict(edit_comment)}
        )
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="Comment Edited!"), 201


@jwt_required
@comment_bp.route("/delete/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    isAdmin = verify_admin_role(current_user)

    try:
        comment_id = create_id(comment_id)
        user_id = create_id(current_user, "_id")
    except InvalidIdException as invalidId:
        return jsonify(message=str(invalidId)), 403

    exitsing_comment = comments_collection.find_one({"_id": comment_id})

    if not exitsing_comment:
        return jsonify(message="Could not find the comment!"), 404

    if not isAdmin and (exitsing_comment["userId"] != str(user_id)):
        return jsonify(message="You are not allowed to perform this task!"), 401

    try:
        comments_collection.find_one_and_delete({"commentId": comment_id})
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="Comment Deleted!"), 201


@jwt_required
@comment_bp.route("/retreive", methods=["GET"])
def retreive_comment():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    is_admin = verify_admin_role(current_user)

    try:
        user_id = create_id(current_user, "_id")
    except InvalidIdException as invalidId:
        return jsonify(message=str(invalidId)), 403

    all_comments_of_user = object_id_to_string(
        list(comments_collection.find({"userId": str(user_id)}))
    )

    try:
        if is_admin:
            all_other_comments = object_id_to_string(
                list(comments_collection.find({"userId": {"$ne": str(user_id)}}))
            )
            return (
                jsonify(
                    your_comments=all_comments_of_user,
                    all_other_comments=all_other_comments,
                ),
                200,
            )

        if not all_comments_of_user:
            return jsonify(message="You do not have any comments"), 404

        return jsonify(all_comments_of_user), 200

    except Exception as e:
        return jsonify(message=f"Server error!, {str(e)}"), 500
