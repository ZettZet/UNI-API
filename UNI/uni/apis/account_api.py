import bcrypt
from bson import ObjectId
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
    fresh_login_required,
)
from flask_restx import Namespace, Resource, fields, reqparse
from mongoengine import Document, DoesNotExist, NotUniqueError, StringField, connect

from .extra import ObjectIdField

login_manager = LoginManager()

account_ns = Namespace("account", description="Global route to work with accounts")
account_ns.add_model("Message", "Standart model for no-resourse responses")
users_db = connect("users", alias="users_alias", host="mongodb://mongo:27017")


@login_manager.user_loader
def load_user(user_id):
    try:
        return Account.objects.get(id=ObjectId(user_id))
    except DoesNotExist:
        return None


def gen_hash(psw: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(psw.encode("utf8"), salt)


def check_hash(hash: str, psw: str) -> bool:
    return bcrypt.checkpw(psw.encode("utf8"), hash.encode("utf8"))


message = account_ns.model(
    "Message", {"message": fields.String("Description of response")},
)


account = account_ns.model(
    "Account",
    {
        "id": ObjectIdField,
        "username": fields.String(required=True),
        "password_hash": fields.String(required=True),
        "role": fields.String(
            description="Possible three states: USER, MODER, ADMIN", default="USER"
        ),
    },
    mask="id,username,role",
)


@account_ns.route("/login/", doc={"description": "Login user, accept 2 args"})
class Login(Resource):
    login_parser = (
        reqparse.RequestParser()
        .add_argument("username", type=str, required=True, location="form")
        .add_argument("password", type=str, required=True, location="form")
    )

    @account_ns.response(401, "User not found", model=message)
    @account_ns.response(400, "Incorrect password", model=message)
    @account_ns.response(200, "Logged in successfuly", model=message)
    @account_ns.expect(login_parser)
    def post(self):
        args = self.login_parser.parse_args()

        try:
            found_user = Account.objects.get(username=args["username"])

            if check_hash(found_user.password_hash, args["password"]) == True:
                login_user(found_user)

                return {"message": "Login successful"}, 200

            else:
                return {"message": "Incorrect password"}, 400

        except DoesNotExist as dne:
            return {"message": format(dne)}, 401


@account_ns.route("/signup/")
class SignUp(Resource):
    signup_parser = (
        reqparse.RequestParser()
        .add_argument("username", type=str, required=True, location="form")
        .add_argument("password", type=str, required=True, location="form")
    )

    @account_ns.response(409, "User already exists", model=message)
    @account_ns.response(201, "Success, account registered", model=message)
    @account_ns.expect(signup_parser)
    def post(self):
        args = self.signup_parser.parse_args()

        try:
            new_user = Account(
                username=args["username"], password_hash=gen_hash(args["password"])
            )
            new_user.save()

            return {"message": "Sign up success"}, 201

        except NotUniqueError as nue:
            return {"message": f"Not unique login. User already exist {nue}"}, 409


@account_ns.route("/logout/")
class Logout(Resource):
    @account_ns.response(200, "Logout success", model=message)
    @account_ns.response(
        401,
        'When try to force logout ("force" same as "without logging in")',
        model=message,
    )
    @login_required
    def get(self):
        return {"message": f"{logout_user()}"}


@account_ns.route(
    "/", doc={"description": "Returns all accounts (without password_hash)"}
)
class Accounts(Resource):
    @account_ns.marshal_list_with(account)
    def get(self):
        return [item for item in Account.objects]


@account_ns.route("/<string:id>/")
class AccountCabinet(Resource):
    @account_ns.doc(description="Returns valid Account JSON, else 404")
    @account_ns.response(404, description="Not found account with id", model=message)
    @account_ns.response(200, description="Success", model=account)
    def get(self, id):
        try:
            return (
                account_ns.marshal(Account.objects.get(id=ObjectId(id)), account),
                200,
            )
        except Exception as dne:
            return {"message": "User not found"}, 404

    @account_ns.doc(
        description="Deletes only when user wants to delete their account or ADMIN decided to delete "
    )
    @account_ns.response(200, "Deleted", model=message)
    @account_ns.response(403, "Not self account", model=message)
    @account_ns.response(401, "Unauthorized", model=message)
    @account_ns.response(404, "Not found account with id", model=message)
    @fresh_login_required
    def delete(self, id):
        try:
            found_user = Account.objects.get(id=ObjectId(id))

            if id == current_user.get_id() or current_user.role == "ADMIN":
                if current_user.role != "ADMIN":
                    logout_user()

                found_user.delete()

                return {"message": "Deleted"}, 200

            return {"message": "Not Enough Permission"}, 403

        except DoesNotExist:
            return {"message": "User not found"}, 404

    @fresh_login_required
    def put(self, id):
        pass


class Account(UserMixin, Document):
    username = StringField(max_length=35, unique=True, required=True)
    password_hash = StringField(max_length=70, required=True)
    role = StringField(max_length=5, default="USER")

    meta = {"db_alias": "users_alias", "collection": "users"}
