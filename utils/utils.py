from bson import ObjectId
from custom_exceptions import InvalidIdException
import json

def verify_admin_role(current_user):
    if type(current_user) == str:
        current_user = json.loads(current_user)
    admin = current_user["isAdmin"]
    if not admin:
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


def create_id(obj, id=None):
    try:
        if not id:
            return ObjectId(obj)
    except Exception:
        raise InvalidIdException(f"The given id is invalid")
    try:
        if id not in obj:
            return None
        if "_id" in id:
            return obj[id]
        return ObjectId(obj[id])
    except Exception:
        raise InvalidIdException(f"The given {id} is invalid")
