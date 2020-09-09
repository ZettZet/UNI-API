from flask_login import UserMixin
from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    StringField,
)


class Account(UserMixin, Document):
    username = StringField(max_length=35, unique=True, required=True)
    password_hash = StringField(max_length=70, required=True)
    role = StringField(max_length=5, default="USER")

    meta = {"collection": "users", "db_alias": "uni_alias"}


class Example(EmbeddedDocument):
    ExampleText = StringField()
    Source = StringField()
    Uri = StringField(default="", null=True)


class Data(EmbeddedDocument):
    Header = StringField(required=True)
    Termin = StringField(required=True)
    Definition = StringField(required=True)
    Examples = EmbeddedDocumentListField(Example)


class Article(Document):
    EnglishPart = EmbeddedDocumentField(Data)
    RussianPart = EmbeddedDocumentField(Data)

    meta = {"collection": "articles", "db_alias": "uni_alias"}
