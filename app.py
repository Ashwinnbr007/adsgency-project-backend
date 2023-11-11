from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from routes.users import user_bp
from routes.books import book_bp

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# Register endpoint blueprints
app.register_blueprint(user_bp)
app.register_blueprint(book_bp)


@app.route("/")
def hello_world():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True)
