from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from pydantic import ValidationError
from models.comment import Comment
from mongo_connection import comments_collection, books_collection
from utils.utils import object_id_to_string, verify_admin_role

comment_bp = Blueprint("comments", __name__, url_prefix="/comments")


@jwt_required
@comment_bp.route("/create", methods=["POST"])
def register():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    comment_data = request.get_json()
    id = comments_collection.count_documents({}) + 1

    bookExists = books_collection.find_one({"bookId": comment_data["bookId"]})
    if not bookExists:
        return jsonify(message="The book does not exist"), 404

    try:
        new_comment = Comment(
            commentId=id, userId=current_user["userId"], **comment_data
        )
        comments_collection.insert_one(dict(new_comment))
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="Comment added!"), 201


@jwt_required
@comment_bp.route("/edit/<comment_id>", methods=["PUT"])
def edit_comment(comment_id: int):
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    comment_data = request.get_json()

    exitsing_comment = comments_collection.find_one({"commentId": int(comment_id)})

    if not exitsing_comment:
        return jsonify(message="Could not find the comment!"), 404

    try:
        edit_comment = Comment(
            userId=current_user["userId"],
            bookId=exitsing_comment["commentId"],
            reviewId=exitsing_comment["reviewId"],
            commentId=int(comment_id),
            **comment_data,
        )
        comments_collection.find_one_and_update(
            {"commentId": int(comment_id)}, {"$set": dict(edit_comment)}
        )
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="Comment Edited!"), 201


@jwt_required
@comment_bp.route("/delete/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id: int):
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    isAdmin = verify_admin_role(current_user)

    exitsing_comment = comments_collection.find_one({"commentId": int(comment_id)})

    if not exitsing_comment:
        return jsonify(message="Could not find the comment!"), 404

    if not isAdmin and (exitsing_comment["userId"] != current_user["userId"]):
        return jsonify(message="You are not allowed to perform this task!"), 401

    try:
        comments_collection.find_one_and_delete({"commentId": int(comment_id)})
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

    all_comments_of_user = object_id_to_string(
        list(comments_collection.find({"userId": int(current_user["userId"])}))
    )

    try:
        if is_admin:
            all_comments = object_id_to_string(list(comments_collection.find({})))
            return (
                jsonify(your_comments=all_comments_of_user, all_comments=all_comments),
                200,
            )

        if not all_comments_of_user:
            return jsonify(message="You do not have any comments"), 404

        return jsonify(all_comments_of_user), 200

    except Exception as e:
        return jsonify(message=f"Server error!, {str(e)}"), 500
