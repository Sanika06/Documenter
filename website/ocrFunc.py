import os
import re
import cv2
import nltk
import easyocr
import langid
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app as app

ocrFunc = Blueprint('ocrFunc', __name__)
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}

# def pdf_to_images(pdf_path):
#     pdf_document = fitz.open(pdf_path)
#     images = []
#     for page_num in range(pdf_document.page_count):
#         page = pdf_document.load_page(page_num)
#         image = page.get_pixmap()
#         image = Image.frombytes("RGB", (image.width, image.height), image.samples)
#         images.append(image)
#     return images


@ocrFunc.route("/scanning", methods=['GET','POST'])
def scanning():
    filename = request.args.get('file_path')
    extension = os.path.splitext(filename)[1]
    # print(extension)

    if extension not in ALLOWED_EXTENSIONS:
        flash('File type not allowed. Please upload a file with one of the following extensions: {}'.format(", ".join(ALLOWED_EXTENSIONS)))
        return redirect(url_for("views.dashboard"))

    contentFound = ""
    # if filename.lower().endswith('.pdf'):  #PDF needs to be taken care of.
    #     filename = pdf_to_image(filename)
        
    reader = easyocr.Reader(['en', 'de', 'fr'])
    result = reader.readtext(filename)
    for detection in result:
        contentFound += detection[1]

    language = langid.classify(contentFound)
    # print("Detected language:", language)

    return render_template("ocrFunctions.html", text=contentFound)

            