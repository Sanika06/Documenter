from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class register_info(db.Model, UserMixin):
    Name = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(50), nullable=False, primary_key=True)
    Phone_no = db.Column(db.String(10), nullable=False)
    Password = db.Column(db.String(50), nullable=False)

class queryAndFeedback(db.Model, UserMixin):
    No = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Email = db.Column(db.String(50), nullable=False)
    Feedback = db.Column(db.String(100), nullable=False)
    
class receiptContents(db.Model, UserMixin):
    RecieptNo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Title = db.Column(db.String(25))
    Date = db.Column(db.String(7))
    Total = db.Column(db.String(15))
    PhoneNO = db.Column(db.String(10))
    Contents = db.Column(db.String(100))  # Add Contents column
    Purpose = db.Column(db.String(50))
