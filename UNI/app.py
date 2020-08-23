from flask import Flask
from flask.wrappers import Response
from mongoengine import connect
from mongoengine.connection import disconnect

from uni.apis import api, login_manager

app = Flask(__name__)
app.secret_key = b"somesecretkey"

login_manager.init_app(app)
api.init_app(app)

debug_flag: bool = False


@app.before_request
def before():
    try:
        db = connect(db="articles", alias="uni_alias", host=(
            "localhost" if debug_flag else "mongo"), port=27017)
    except:
        print("!")


@app.after_request
def after(response: Response):
    disconnect(alias='uni_alias')

    return response


if __name__ == "__main__":
    app.run(debug=debug_flag)
