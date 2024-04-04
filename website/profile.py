from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app as app, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import os

from . import db
from .models import register_info,queryAndFeedback

profile = Blueprint('profile', __name__)


@profile.route("/profilePage", methods=['GET','POST'])
def profilePage():
    if request.method == 'POST':
        action = request.form.get('action')
        # print(action)
        if action == 'editPersonalDetails':
            return redirect(url_for('profile.editPersonalDetails'))
        elif action == 'viewMyDocs':
            return redirect(url_for('profile.viewMyDocs'))
        elif action == 'viewStandardDocs':
            return redirect(url_for('profile.viewStandardDocs'))
        elif action == 'queryandfeedback':
            return redirect(url_for('profile.queryandfeedback'))
    return render_template("userProfile.html")

@profile.route("/editPersonalDetails", methods=['GET','POST'])
def editPersonalDetails():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        flag = 0  
        if name == "" or len(phone) < 10 or password == "":
            flash("Invalid Input", category="error")
        elif len(password) < 6:
            for i in password:
                if i.isupper() or i.islower():
                    flag += 1
            if flag != 2:
                    flash("Invalid password Entered :  (Req - 1 Upper and 1 lower case letter)", category="error")
        else:
            userId = session.get('user-id')
            # print(userId)
            user = register_info.query.filter_by(Email=userId).first()
            if user:
                user.Name = name
                user.Phone_no = phone
                user.Password = generate_password_hash(password, method='pbkdf2:sha256')
                db.session.commit()
                flash("User details updated successfully", category="success")
            else:
                flash("SOME ERROR OCCURED")
        return redirect(url_for('views.login')) 
    return render_template("editPersonalDetails.html")


@profile.route("/viewMyDocs", methods=['GET','POST'])
def viewMyDocs():
   
    userId = session.get('user-id')
    folder_path = os.path.join("E:\\Projects\\Documenter\\uploads", userId, "org")
    try:
        files = os.listdir(folder_path)
        return render_template('viewMyDocs.html', files=files)
    except FileNotFoundError:
        flash("No Files Found")
    return redirect(url_for("profile.profilePage"))

@profile.route('/open_file/<file_name>')
def open_file(file_name):
    userId = session.get('user-id')
    folder_path = os.path.join("E:\\Projects\\Documenter\\uploads", userId, "org")
    file_path = folder_path +"\\" + file_name
    return send_file(file_path, as_attachment=True)

@profile.route("/viewStandardDocs")
def viewStandardDocs():
    userId = session.get('user-id')
    folder_path = os.path.join("E:\\Projects\\Documenter\\uploads", userId, "std")
    try:
        files = os.listdir(folder_path)
        return render_template('viewStandardDocs.html', files=files)
    except FileNotFoundError:
        flash("No Files Found")
    return redirect(url_for("profile.profilePage"))

@profile.route('/open_stdfile/<file_name>')
def open_stdfile(file_name):
    userId = session.get('user-id')
    folder_path = os.path.join("E:\\Projects\\Documenter\\uploads", userId, "std")
    file_path = folder_path +"\\" + file_name
    return send_file(file_path, as_attachment=True)

@profile.route("/queryandfeedback", methods=['GET','POST'])
def queryandfeedback():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == "submit":
            userID = session.get('user-id')
            Email = userID
            Feedback = request.form.get("feedback")
            if Feedback != "":
                newFeedback = queryAndFeedback(Email = Email, Feedback = Feedback)
                db.session.add(newFeedback)
                db.session.commit()
                flash('Feedback Submitted', category='success')
                return redirect(url_for("views.dashboard"))
    return render_template("queryAndFeedback.html")