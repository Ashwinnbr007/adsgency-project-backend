from flask import jsonify


def verify_admin_role(current_user):
    role = current_user["role"]
    print(role)
    if role != "admin":
        return False
    return True
