# type: ignore

from bson import ObjectId
from flask_restx import Namespace, Resource, fields
from mongoengine import errors

from .db_models import Specialist
from .extra import ObjectIdField

specialist_ns = Namespace(
    "specialist", description="Global route to work with specialists")

specialist = specialist_ns.model("Specialist", {
    "id": ObjectIdField(allow_null=True),
    "FirstName": fields.String,
    "SecondName": fields.String,
    "MiddleName": fields.String,
    "Description": fields.List(fields.String, description="List of paragraphs"),
    "PhotoUri": fields.String,
    "FullName": fields.String
})

message = specialist_ns.model(
    "Message", {"message": fields.String("Description of response"), },
)


def form(item: Specialist):
    return {**item.to_mongo(), 'id': item.id, 'FullName': f'{item.SecondName} {item.FirstName} {item.MiddleName}'}


@specialist_ns.route('/')
class Specislists(Resource):

    @specialist_ns.marshal_list_with(specialist, code=200)
    def get(self):
        return [form(item) for item in Specialist.objects()]


@specialist_ns.route('/<string:id>/', doc={"params": {"id": "ObjectID string"}})
class SpecialistOne(Resource):

    @specialist_ns.response(415, "Invalid ObjectID", model=message)
    @specialist_ns.response(200, "Success", model=specialist)
    def get(self, id):
        try:
            spec = Specialist.objects.get(id=ObjectId(id))
            resp = form(spec)
            return specialist_ns.marshal(resp, specialist), 200
        except errors.InvalidId as bs:
            return {"message": format(bs)}, 415
