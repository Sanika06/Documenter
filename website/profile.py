from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app as app

profile = Blueprint('profile', __name__)

@profile.route("/profilePage")
def profilePage():
    return render_template("userProfile.html")

