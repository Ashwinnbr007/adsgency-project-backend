from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from pydantic import ValidationError
from models.comment import Comment
from mongo_connection import comments_collection
from utils.utils import verify_admin_role

comment_bp = Blueprint("comments", __name__, url_prefix="/comments")


@jwt_required
@comment_bp.route("/create", methods=["POST"])
def register():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    comment_data = request.get_json()
    id = comments_collection.count_documents({}) + 1
    try:
        new_comment = Comment(commentId=id, userId=current_user['userId'], **comment_data)
        comments_collection.insert_one(dict(new_comment))
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="Comment added!"), 201
