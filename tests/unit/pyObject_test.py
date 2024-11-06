from app.models.pyObject import PyObjectId
from bson import ObjectId


def test_valid_object_id():
    valid_id = ObjectId()
    validated_id = PyObjectId.validate(valid_id)
    assert validated_id == valid_id, "PyObjectId should validate a valid ObjectId"
