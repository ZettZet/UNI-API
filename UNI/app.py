from flask import Flask, g
from mongoengine import connect
from mongoengine.connection import disconnect

from uni.apis import api, login_manager

app = Flask(__name__)
app.secret_key = b"somesecretkey"

login_manager.init_app(app)
api.init_app(app)

debug_flag: bool = False


@app.before_first_request
def before():
    try:
        g['db'] = connect(db="articles", alias="uni_alias", host=(
            "localhost" if debug_flag else "mongo"), port=27017)
    except:
        print("!")


@app.teardown_appcontext
def after(p0: Exception):
    db = g.pop('db', None)

    if db is not None:
        disconnect(alias='uni_alias')


if __name__ == "__main__":
    app.run(debug=debug_flag)
