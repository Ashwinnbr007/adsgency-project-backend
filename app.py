from flask import Flask
from flask_bcrypt import Bcrypt
from routes.users import auth_bp

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.register_blueprint(auth_bp)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
