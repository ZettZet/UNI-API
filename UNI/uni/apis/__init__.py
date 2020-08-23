from flask_restx import Api

from .account_api import account_ns
from .article_api import article_ns

api = Api(title="UNI-API", description="Simple dictionary API", doc="/apidocs/")

api.add_namespace(account_ns)
api.add_namespace(article_ns)
