from flask import Flask
from mongoengine import connect

from uni.apis import api, login_manager

app = Flask(__name__)
app.secret_key = b"somesecretkey"

login_manager.init_app(app)
api.init_app(app)

debug_flag: bool = False

db = connect("articles", host=("localhost" if debug_flag else "mongo"), port=27017)

if __name__ == "__main__":
    app.run(debug=debug_flag)
