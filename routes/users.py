from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from models.user import CreateUser, User
from mongo_connection import users_collection

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/register", methods=["POST"])
def register():
    from app import bcrypt

    try:
        data = CreateUser(**request.get_json())
    except ValidationError as e:
        return jsonify(message=str(e)), 400

    hashed_password = bcrypt.generate_password_hash(data.password).decode("utf-8")

    id = users_collection.count_documents({}) + 1
    emailExists = users_collection.find_one({"email": data.email})

    if not emailExists:
        new_user = User(
            userId=id,
            username=data.username,
            email=data.email,
            role=data.role,
            password=hashed_password,
        )
        try:
            users_collection.insert_one(dict(new_user))
        except Exception as e:
            return jsonify(message=str(e)), 500

        return jsonify(message="User registered successfully!"), 201

    return (
        jsonify(message="Email already registered, please use a different Email ID!"),
        409,
    )


@user_bp.route("/display", methods=["GET"])
async def get_all_books():
    try:
        all_users = users_collection.find()
        users = []

        for user in all_users:
            user["_id"] = str(user["_id"])
            users.append(user)

        return jsonify(users), 200
    except Exception as e:
        return (
            jsonify(message=f"Server Error!, {str(e)}"),
            500,
        )


@user_bp.route("/display/<id_or_email>", methods=["GET"])
async def get_user(id_or_email: str):
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
        user["_id"] = str(user["_id"])
        return jsonify(user), 200
    except Exception as e:
        return (
            jsonify(message=f"Server Error!, {str(e)}"),
            500,
        )
