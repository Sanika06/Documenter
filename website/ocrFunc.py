import os
import re
import cv2
import nltk
from nltk.corpus import wordnet
import easyocr
import langid
import pytesseract
from . import db
from PIL import Image
from werkzeug.utils import secure_filename
from .models import receiptContents
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

def processData(contentFound):
    text = ' '.join(contentFound)

    # Regular expressions for extracting information
    title_pattern = r"(?:Student|Name of Student): ([A-Za-z\s]+)"
    date_pattern = r"(?:Date|Academic): (\d{1,2}/\d{1,2}-\d{2}\s\d{2})"
    total_pattern = r"Total: (\d+)"
    phone_pattern = r"Mobile No(\d{10})"

    # Extracting information using regular expressions
    title_match = re.search(title_pattern, text)
    date_match = re.search(date_pattern, text)
    total_match = re.search(total_pattern, text)
    phone_match = re.search(phone_pattern, text)

    # Displaying extracted information
    if title_match:
        print("Title:", title_match.group(1))
    if date_match:
        print("Date:", date_match.group(1))
    if total_match:
        print("Total:", total_match.group(1))
    if phone_match:
        print("Phone Number:", phone_match.group(1))
    
 
# def translateData(contentFound):

    

@ocrFunc.route("/scanning", methods=['GET','POST'])
def scanning():
    filename = request.args.get('file_path')
    extension = os.path.splitext(filename)[1]
    # print(extension)

    if extension not in ALLOWED_EXTENSIONS:
        flash('File type not allowed. Please upload a file with one of the following extensions: {}'.format(", ".join(ALLOWED_EXTENSIONS)))
        return redirect(url_for("views.dashboard"))

    # if filename.lower().endswith('.pdf'):  #PDF needs to be taken care of.
    #     filename = pdf_to_image(filename)
    contentFound = []
    
    reader = easyocr.Reader(['en', 'de', 'fr'])
    result = reader.readtext(filename)
    for detection in result:
        contentFound.append(detection[1])

    # language = langid.classify(contentFound) // contentFound is a list now, FIX THIS
    # if(language == 'en'):
    processData(contentFound)
    # else:
        # translatedData = translateData(contentFound)
        # processData(translatedData)
        
    
        
    # print("Detected language:", language)
    extractedData = []
    contents = request.form.get('contents')
    purpose = request.form.get('purpose')
    newReceipt = receiptContents(Title = extractedData[0], Date = extractedData[1], Total = extractedData[2] ,PhoneNO = extractedData[0] ,Contents = contents, Purpose = purpose)
    db.session.add(newReceipt)
    db.commit()
    return render_template("ocrFunctions.html", text=extractedData)

            