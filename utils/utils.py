def verify_admin_role(current_user):
    role = current_user["role"]
    if role != "admin":
        return False
    return True


def object_id_to_string(data):
    data["_id"] = str(data["_id"])
    return data
