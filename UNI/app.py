from flask import Flask

from uni.apis import api, login_manager

app = Flask(__name__)
app.secret_key = b"somesecretkey"

login_manager.init_app(app)
api.init_app(app)


if __name__ == "__main__":
    app.run(debug=True)
