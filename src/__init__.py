#import modules
from flask import Flask
import os
from src.auth import auth
from src.bookmarks import bookmarks

#create setups and configurations
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    #check if the application is running test configs
    if test_config is None:

        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY")
        )
    else:
        app.config.from_mapping(test_config)

    #register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)
    return app