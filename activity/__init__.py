"""Initialize app."""

import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()

os.environ["DATABASE_URL"] = 'postgres://ljpnibwjkkajyu:95c9d689a20bf27a0b03d61b1b8a7941e6c0f1698ac6680b260af979bb0bd96a@ec2-52-87-135-240.compute-1.amazonaws.com:5432/d1f0djqlpulvb8'


def create_app():
    """Construct the core app object."""
    app = Flask(__name__)

    # Application Configuration
    app.config.from_mapping(
        #SEND_FILE_MAX_AGE_DEFAULT = 0,
        SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev_key',
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(app.instance_path, 'activity.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # Initialize Plugins
    db.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    with app.app_context():
        from .models import User

        @login_manager.user_loader
        def load_user(user_id):
            # since the user_id is just the primary key of our user table, use it in the query for the user
            return User.query.get(int(user_id))

        # blueprint for auth routes in our app
        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint)

        # blueprint for non-auth parts of app
        from .main import main as main_blueprint
        app.register_blueprint(main_blueprint)

        # Create Database Models
        db.create_all()

        return app
