#import modules
from flask import Flask
import os
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db
from flask_jwt_extended import JWTManager


#create setups and configurations
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    #check if the application is running test configs
    if test_config is None:

        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY')
        )
    else:
        app.config.from_mapping(test_config)

    #set up database
    db.app=app
    db.init_app(app)

    #set up JWT
    JWTManager(app)

    #register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)
    return app