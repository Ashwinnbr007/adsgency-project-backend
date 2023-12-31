from datetime import timedelta
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from routes.users import user_bp
from routes.books import book_bp
from routes.comments import comment_bp
from routes.reviews import reviews_bp

app = Flask(__name__)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(weeks=1)
CORS(app)
bcrypt = Bcrypt(app)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
app.register_blueprint(user_bp)
app.register_blueprint(book_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(reviews_bp)


@app.route("/")
def hello_world():
    return "Welcome to the AdsGency Backend Project, <br> <a href='https://github.com/Ashwinnbr007/adsgency-project-backend'>Github Link</a>"


if __name__ == "__main__":
    app.run(debug=True)
