from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from models.user import CreateUser
from mongo_connection import users_collection

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    from app import bcrypt

    try:
        data = CreateUser(**request.get_json())
    except ValidationError as e:
        return jsonify(message=str(e)), 400

    hashed_password = bcrypt.generate_password_hash(data.password).decode("utf-8")

    new_user = {
        "username": data.username,
        "email": data.email,
        "password": hashed_password,
        "role": "user",
    }

    try:
        users_collection.insert_one(new_user)
    except Exception as e:
        return jsonify(message=str(e)), 500

    return jsonify(message="User registered successfully!"), 201
