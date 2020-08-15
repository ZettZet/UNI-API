import json
import re

from bson import ObjectId
from flask_restx import Model, fields


def check_lang(text: str) -> bool:
    return bool(re.search("[а-яА-Я]", text))


class ObjectIdField(fields.Raw):
    __schema_type__ = "string"
    

    def format(self, value):
        if isinstance(value, ObjectId):
            return str(value)
        else:
            raise fields.MarshallingError(Exception())
