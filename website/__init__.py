from os import path
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, url_for, Blueprint, render_template, Flask

db = SQLAlchemy()
DB_NAME = "Documenter.db"

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def createApp():
    app = Flask(__name__)
    app.config['SECRET_KEY'] ="123"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    from .models import register_info
    from .models import queryAndFeedback
    from .models import receiptContents
    from .views import views
    from .ocrFunc import ocrFunc
    from .profile import profile
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(ocrFunc, url_prefix='/')
    app.register_blueprint(profile, url_prefix='/')
    db.init_app(app)
    create_db(app)
    return app

def create_db(app):
    if not path.exists('website/' +DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database')
    return