from flask_restx import Api

from .account_api import account_ns, login_manager
from .article_api import article_ns
from .specialist_api import specialist_ns

api = Api(title="UNI-API", description="Simple dictionary API",
          prefix='/api', doc="/api/docs/")

api.add_namespace(account_ns)
api.add_namespace(article_ns)
api.add_namespace(specialist_ns)
