def verify_admin_role(current_user):
    role = current_user["role"]
    if role != "admin":
        return False
    return True


def object_id_to_string(data):
    if type(data) == list:
        new_data = []
        for ids in data:
            ids["_id"] = str(ids["_id"])
            new_data.append(ids)
        return new_data

    data["_id"] = str(data["_id"])
    return data
