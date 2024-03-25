import re
import os
import cv2
from .ocrFunc import scanning
from .models import register_info
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for, Blueprint, render_template, request, flash, current_app as app

views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@views.route("/dashboard", methods=['GET', 'POST'])
def dashboard():

    if request.method == 'POST':
        file = request.files['fileToUpload']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for("ocrFunc.scanning", file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)))
        else:
            flash('Some Error Occurred')
            return redirect(request.url)

    return render_template("dashboard.html")

@views.route("/login", methods=['GET','POST'])
def login():

    if request.method == "POST":
        email = request.form.get('Email')
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
        print(loginbutton)
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
            if flag != 3:
                flash("Invalid password", category="error")
        elif not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            flash("Invalid Email id", category="error")

        else:
            from . import db
            new_registeration = register_info(Name=name, Email=email, Phone_no=phone, Password=generate_password_hash(passwd, method='pbkdf2:sha256'))
            db.session.add(new_registeration)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('views.login'))

    return render_template("registerPage.html")
