# type:ignore
import re

from bson import ObjectId, errors
from flask_login import current_user, fresh_login_required
from flask_restx import Namespace, Resource, fields, reqparse
from mongoengine import (
    DoesNotExist,
    connect,
)

from .db_models import Article
from .extra import ObjectIdField, check_lang

article_ns = Namespace(
    "articles", description="Global route to work with articles")


message = article_ns.model(
    "Message", {"message": fields.String("Description of response"), },
)


example = article_ns.model(
    "Example",
    {
        "ExampleText": fields.String,
        "Source": fields.String,
        "Uri": fields.String(default=""),
    },
)

data = article_ns.model(
    "Data",
    {
        "Header": fields.String(required=True),
        "Termin": fields.String(required=True),
        "Definition": fields.String(required=True),
        "Examples": fields.Nested(example, as_list=True),
    },
)

article = article_ns.model(
    "Article",
    {
        "id": ObjectIdField(allow_null=True),
        "EnglishPart": fields.Nested(data),
        "RussianPart": fields.Nested(data),
    },
)

articel_edit_payload = article_ns.model(
    "Article to edit",
    {"EnglishPart": fields.Nested(data), "RussianPart": fields.Nested(data), },
)

most_offten = article_ns.model(
    "Most offten search",
    {"id": ObjectIdField(), "name": fields.String(), },
)


@article_ns.route(
    "/search/",
    doc={
        "description": "Takes string, returns all Articles with a to_search in the Header or Definition. Language doesn`t matter"
    },
)
class ArticleSearch(Resource):
    search_parser = reqparse.RequestParser().add_argument(
        "to_search", type=str, required=True, location="args"
    )

    @article_ns.marshal_list_with(
        article,
        code=200,
        description="All okay (By default returns not all fields, look at the mask (X-Fields))",
        mask="id, EnglishPart{Header,Definition},RussianPart{Header,Definition}",
    )
    @article_ns.expect(search_parser)
    def get(self):
        to_search = self.search_parser.parse_args().get("to_search")
        is_russian = check_lang(to_search)

        regex = re.compile(fr'(?<![\wа-я])({to_search})', re.IGNORECASE)

        settings = {True: {
            'RussianPart.Termin': regex,
        },
            False: {
            'EnglishPart.Termin': regex,
        }}

        temp = [item for item in Article.objects(__raw__=settings[is_russian])]

        def sort(article):
            if is_russian:
                return article.RussianPart.Termin.lower().index(to_search)
            else:
                return article.EnglishPart.Termin.lower().index(to_search)

        temp = sorted(temp, key=sort)

        return (temp, 200)


@article_ns.route("/")
class ArticleList(Resource):
    @article_ns.doc(description="Returns all articles from DB")
    @article_ns.marshal_list_with(article)
    def get(self):
        return [item for item in Article.objects], 200

    @article_ns.doc(description="Create article")
    @article_ns.response(201, "Created")
    @article_ns.response(
        400,
        "Validation error: required parameter was missed or invalid parameter was provided",
    )
    @article_ns.expect(articel_edit_payload, validate=True)
    def post(self):
        Article.from_json(json.dumps(article_ns.payload)).save()

        return {"message": "Created"}, 201


@article_ns.route("/<string:id>/", doc={"params": {"id": "ObjectID string"}})
class ArticleResource(Resource):
    @article_ns.doc(description="Returns valid Article JSON, else 415")
    @article_ns.response(415, "Invalid ObjectID", model=message)
    @article_ns.response(200, "Success", model=article)
    def get(self, id):
        try:
            return (
                article_ns.marshal(Article.objects.get(
                    id=ObjectId(id)), article),
                200,
            )

        except errors.InvalidId as bs:
            return {"message": format(bs)}, 415

    @article_ns.response(200, "Deleted", model=message)
    @article_ns.response(403, "Not MODER or ADMIN", model=message)
    @article_ns.response(401, "Unauthorized", model=message)
    @article_ns.response(404, "Not found account with id", model=message)
    @fresh_login_required
    def delete(self, id):
        try:
            found_article = Article.objects.get(id=ObjectId(id))

            if current_user.role in ["ADMIN", "MODER"]:
                found_article.delete()
                return {"message": "Deleted"}, 200

            return {"message": "Not Enough Permission"}, 403
        except DoesNotExist:
            return {"message": "Article not found"}, 404

    @article_ns.doc(
        description="Update existing resource (NOT IMPLEMENTED YET)",
    )
    @article_ns.expect(articel_edit_payload, validate=True)
    # TODO
    def put(self, id):
        pass


@article_ns.route('/most_offten')
class ArticleMostOfften(Resource):

    @article_ns.marshal_list_with(most_offten)
    def get(self):
        temp = [ObjectId('5f9b3d9949e7b01c10a22be7'), ObjectId(
            '5f9b3d9949e7b01c10a22be1'), ObjectId('5f9b3d9949e7b01c10a22bf8'), ObjectId('5f9b3d9949e7b01c10a22bff'), ObjectId('5f9b3d9949e7b01c10a22c0d')]
        return [{'id': item, 'name': Article.objects(
            id=item).EnglishPart.Title} for item in temp]
