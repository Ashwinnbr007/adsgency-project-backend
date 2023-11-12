from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
)
from utils.utils import object_id_to_string, verify_admin_role
from pydantic import ValidationError
from models.user import User
from mongo_connection import users_collection

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/register", methods=["POST"])
def register():
    from app import bcrypt

    user_data = request.get_json()

    hashed_password = bcrypt.generate_password_hash(user_data["password"]).decode(
        "utf-8"
    )

    id = users_collection.count_documents({}) + 1
    email_exists = users_collection.find_one({"email": user_data["email"]})
    user_exists = users_collection.find_one({"username": user_data["username"]})

    if email_exists:
        return (
            jsonify(
                message="Email already registered, please use a different Email ID!"
            ),
            409,
        )

    if user_exists:
        return (
            jsonify(
                message="Username already registered, please use a different username!"
            ),
            409,
        )

    try:
        new_user = User(
            userId=id,
            username=user_data["username"],
            email=user_data["email"],
            role=user_data["role"],
            password=hashed_password,
        )
        users_collection.insert_one(dict(new_user))
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="User registered successfully!"), 201


@user_bp.route("/login", methods=["POST"])
def login():
    from app import bcrypt

    data = request.get_json()

    if "email" in data:
        identity_method = {"email": data.get("email")}
    else:
        identity_method = {"username": data.get("username")}

    password = data.get("password")

    user = users_collection.find_one(identity_method)

    if user and bcrypt.check_password_hash(user["password"], password):
        del user["_id"]
        del user["password"]
        access_token = create_access_token(identity=user)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401


@jwt_required()
@user_bp.route("/display", methods=["GET"])
async def get_all_books():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    if not verify_admin_role(current_user):
        return (
            jsonify(message="You are not permitted to perform this action!"),
            401,
        )
    try:
        all_users = users_collection.find()
        users = []

        for user in all_users:
            user = object_id_to_string(user)
            users.append(user)

        return jsonify(users), 200
    except Exception as e:
        return (
            jsonify(message=f"Server Error!, {str(e)}"),
            500,
        )


@jwt_required()
@user_bp.route("/display/<id_or_email>", methods=["GET"])
async def get_user(id_or_email: str):
    verify_jwt_in_request()
    current_user = get_jwt_identity()

    if not verify_admin_role(current_user):
        return (
            jsonify(message="You are not permitted to perform this action!"),
            401,
        )

    if "@" in id_or_email:
        search = {"email": id_or_email}
    else:
        search = {"userId": int(id_or_email)}

    try:
        user = users_collection.find_one(search)
        if not user:
            return (
                jsonify(message=f"User {search} doesnt exist."),
                404,
            )
        user = object_id_to_string(user)
        return jsonify(user), 200
    except Exception as e:
        return (
            jsonify(message=f"Server Error!, {str(e)}"),
            500,
        )
