import os
import re
import cv2
import nltk
import easyocr
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app as app

ocrFunc = Blueprint('ocrFunc', __name__)

@ocrFunc.route("/scanning", methods=['GET','POST'])
def scanning():
    filename = request.args.get('file_path')
    reader = easyocr.Reader(['en'])
    result = reader.readtext(filename)
    contentFound = ""
    for detection in result:
        contentFound += detection[1]

    return render_template("ocrFunctions.html", text = contentFound)