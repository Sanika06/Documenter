import re
import os
import cv2
from .ocrFunc import scanning
from .models import register_info, receiptContents
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for, Blueprint, render_template, request, flash, current_app as app, session

views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route("/viewMyInfo", methods=['GET', 'POST'])

def viewMyInfo():
    if request.method == 'POST':
        userId = session.get('user-id') 
        option = request.form.get("option")

        if option == "id":
            id = request.form.get("input")
            records = receiptContents.query.filter_by(Email=userId, RecieptNo=id).all()
        elif option == "purpose":
            purpose = request.form.get("input")
            records = receiptContents.query.filter_by(Email=userId, Purpose=purpose).all()
        else:
            records = receiptContents.query.filter_by(Email=userId).all()
        
        if not records:
            flash("No Data Found")
            return redirect(url_for("views.viewMyInfo"))
        else:
            return render_template("viewMyInfo.html", records=records)

    return render_template("viewMyInfo.html")

@views.route("/dashboard", methods=['GET', 'POST'])
def dashboard():

    userId = session.get('user-id')
    name = ""
    if userId:
        name = register_info.query.filter_by(Email = userId).first()
        if name:
            name = name.Name
        # print(name)
   
    if request.method == 'POST':
        if 'action' in request.form:
            action = request.form['action']
            if action == 'viewMyInfo':
                return redirect(url_for("views.viewMyInfo"))
        else:
            file = request.files['fileToUpload']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                newPath = os.path.join(app.config['UPLOAD_FOLDER'], userId)
                newPath = os.path.join(newPath, 'org')
                if not os.path.exists(newPath):
                    os.makedirs(newPath)
                file.save(os.path.join(newPath, filename))
                return redirect(url_for("ocrFunc.scanning", file_path=os.path.join(newPath, filename)))
    

    return render_template("dashboard.html", text = "Welcome " + name + ", Let's Organize Your World !")

@views.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for("views.register"))

@views.route("/login", methods=['GET','POST'])
def login():

    if request.method == "POST":
        email = request.form.get('Email')
        session['user-id'] = email
        passwd = request.form.get('password')
        registerations = register_info.query.all()
        for var in registerations:
            if email == var.Email:
                if check_password_hash(var.Password, passwd):
                    return redirect(url_for('views.dashboard'))
        flash("Invalid credentials", category="error")
    
    return render_template("user-login.html")

@views.route("/", methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':

        loginbutton = request.form.get('button')
        # print(loginbutton)
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phoneno')
        passwd = request.form.get('Password')

        flag = 0  
        if name == "" or email == "" or len(phone) < 10 or passwd == "":
            flash("Invalid Input", category="error")
        elif len(passwd) < 6:
            for i in passwd:
                if i.isupper() or i.islower():
                    flag += 1
            if flag != 2:
                flash("Invalid password Entered :  (Req - 1 Upper and 1 lower case letter)", category="error")
        elif not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            flash("Invalid Email id", category="error")
        elif register_info.query.filter_by(Email=email).first() and loginbutton == "Register Now":
            flash("Email already exists, try logging in!", category="error")
        else:
            from . import db
            new_registeration = register_info(Name=name, Email=email, Phone_no=phone, Password=generate_password_hash(passwd, method='pbkdf2:sha256'))
            db.session.add(new_registeration)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('views.login'))

    return render_template("registerPage.html")
