from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class register_info(db.Model, UserMixin):
    Name = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(50), nullable=False, primary_key=True)
    Phone_no = db.Column(db.String(10), nullable=False)
    Password = db.Column(db.String(50), nullable=False)
 
