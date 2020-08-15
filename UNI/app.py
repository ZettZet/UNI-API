from flask import Flask
from mongoengine import connect

from uni.apis import api, login_manager

app = Flask(__name__)
app.secret_key = b"somesecretkey"

login_manager.init_app(app)
api.init_app(app)


if __name__ == "__main__":
    debug_flag: bool = True
    db = connect("articles", host=("localhost" if debug_flag == True else "mongo"), port=27017)
    app.run(debug=debug_flag)
