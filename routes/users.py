import json
from bson import ObjectId, json_util
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
)
from custom_exceptions import InvalidIdException
from utils.utils import create_id, object_id_to_string, verify_admin_role
from pydantic import ValidationError
from models.user import User
from mongo_connection import users_collection

user_bp = Blueprint("users", __name__, url_prefix="/users")


@user_bp.route("/create", methods=["POST"])
def register():
    from app import bcrypt

    user_data = request.get_json()

    hashed_password = bcrypt.generate_password_hash(user_data["password"]).decode(
        "utf-8"
    )

    email_exists = users_collection.find_one({"email": user_data["email"]})
    username_exists = users_collection.find_one({"username": user_data["username"]})

    if email_exists:
        return (
            jsonify(
                message="Email already registered, please use a different Email ID!"
            ),
            409,
        )

    if username_exists:
        return (
            jsonify(
                message="Username already registered, please use a different username!"
            ),
            409,
        )

    del user_data["password"]
    try:
        new_user = User(password=hashed_password, **user_data)
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
        identity_method = {"email": data["email"]}
    else:
        identity_method = {"username": data["username"]}

    password = data["password"]

    user = users_collection.find_one(identity_method)

    if user and bcrypt.check_password_hash(user["password"], password):
        del user["password"]
        user = object_id_to_string(user)
        access_token = create_access_token(identity=dict(user))
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401


@jwt_required()
@user_bp.route("/display", methods=["GET"])
def get_all_users():
    verify_jwt_in_request()
    current_user = object_id_to_string(get_jwt_identity())
    is_admin = verify_admin_role(current_user)
    try:
        user_id = create_id(current_user, "_id")
    except InvalidIdException as invalidId:
        return jsonify(message=str(invalidId)), 403

    your_user = object_id_to_string(users_collection.find_one({"_id": user_id}))

    try:
        if is_admin:
            all_other_users = object_id_to_string(
                list(users_collection.find({"_id": {"$ne": user_id}}))
            )
            return (
                jsonify(
                    your_user=your_user,
                    all_other_users=all_other_users,
                ),
                200,
            )

        if not your_user:
            return jsonify(message="Not a user"), 404

        return jsonify(your_user), 200

    except Exception as e:
        return jsonify(message=f"Server error!, {str(e)}"), 500


@jwt_required()
@user_bp.route("/delete/<id_or_email>", methods=["DELETE"])
def delete_users(id_or_email):
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    is_admin = verify_admin_role(current_user)

    if not is_admin:
        return jsonify(message="You are not allowed to perform this action"), 401

    try:
        search = {"_id": create_id(id_or_email)}
    except InvalidIdException:
        search = {"email": id_or_email}

    user = users_collection.find_one(search)
    if not user:
        return jsonify(message="User not found!"), 404

    email = user["email"]
    username = user["username"]

    try:
        users_collection.find_one_and_delete(search)
    except Exception as e:
        return jsonify(message=f"Server error!, {str(e)}"), 500

    return jsonify(message=f"User {username} with email {email} deleted"), 200


@jwt_required()
@user_bp.route("/update/<id_or_email>", methods=["PUT"])
def update_users_admin(id_or_email):
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    is_admin = verify_admin_role(current_user)
    fields = {"email", "password", "username"}
    user_data = request.get_json()

    if not is_admin:
        return jsonify(message="You are not allowed to perform this action"), 401

    try:
        search = {"_id": create_id(id_or_email)}
    except InvalidIdException:
        search = {"email": id_or_email}

    email_exists = users_collection.find_one({"email": user_data["email"]})
    if email_exists:
        return (
            jsonify(
                message="Email already registered, please use a different Email ID!"
            ),
            409,
        )
    username_exists = users_collection.find_one({"username": user_data["username"]})
    if username_exists:
        return (
            jsonify(
                message="Username already registered, please use a different username!"
            ),
            409,
        )

    user_to_edit = users_collection.find_one(search)
    try:
        for field in fields:
            if field not in user_data:
                user_data[field] = user_to_edit[field]

        edit_user = User(
            **user_data,
        )
        users_collection.find_one_and_update(search, {"$set": dict(edit_user)})
    except ValidationError as e:
        return jsonify(message=str(e)), 403
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="User Edited!"), 201
