import re

from enum import Enum
from typing import Any
import bcrypt
from bson import ObjectId
from flask_restx import fields


class Role(Enum):
    User = "USER"
    Moder = "MODER"
    Admin = "ADMIN"

    def __str__(self):
        return self.value


def check_lang(text: str) -> bool:
    return bool(re.search("[а-яА-Я]", text))


def gen_hash(psw: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(psw.encode("utf8"), salt)


def check_hash(hash: str, psw: str) -> bool:
    return bcrypt.checkpw(psw.encode("utf8"), hash.encode("utf8"))


class ObjectIdField(fields.Raw):
    __schema_type__ = "string"

    def format(self, value: Any):
        if isinstance(value, ObjectId):
            return str(value)
        else:
            raise fields.MarshallingError(Exception())
