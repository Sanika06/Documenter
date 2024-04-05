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
from flask import Blueprint, render_template, request, redirect, send_file, url_for, flash, current_app as app
import spacy
from spacy.matcher import Matcher
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas

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

def extract_title(contentFound):
    nlp = spacy.load("en_core_web_sm")
    about_doc = nlp(contentFound)
    matcher = Matcher(nlp.vocab)
    pattern = [{"POS": "PROPN"}]
    matcher.add("TITLE", [pattern])
    matches = matcher(about_doc)
    title = ""
    for _, start, end in matches:
        span = about_doc[start:end]
        title = span.text
        print("TITLE: ", title)
        return title

def extract_date(contentFound):
    date_pattern = re.compile(r'\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:\d{1,2}[-/])?\d{1,2}[-/]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-\s]\d{1,2}(?:st|nd|rd|th)?(?:,\s+\d{2,4})?|\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b(?:day)?(?:,?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))?(?:\s+\d{2,4})?|\d{1,2}:\d{2}\s*(?:a.m.|p.m.)?|\d{1,2}(?:\.\d{2})?\s*(?:a.m.|p.m.|hours)?|(?:\d{1,2}(?:\s*(?:a.m.|p.m.|hours))?|midnight|noon)(?:\s+(?:at\s+)?(?:\d{1,2}:\d{2})?(?:\s*(?:a.m.|p.m.))?)?)\b')

    matches = re.findall(date_pattern, contentFound)
    for match in matches:
        if re.search(r'Date\s?' + re.escape(match), contentFound):
            # print(match)
            return match
        else:
            return "NA"

def extract_phone_numbers(text):
    pattern = r'\b(?:\d{5}[-.\s]??\d{5}|\d{10})\b'
    phone_numbers = re.findall(pattern, text)
    if(phone_numbers):
        print("Phone Number: ", phone_numbers[0])
    return phone_numbers[0] if(phone_numbers) else "NA"

def extract_total(contentFound):
    total_match = re.search(r'(?:Total|Grand\sTotal|Amount|Sub\sTotal|Net\sTotal)\W*?(\d+(\.\d+)?)', contentFound)
    if total_match:
        total_value = total_match.group(1)
        print("Value after 'Total':", total_value)
        return total_value
    else:
        return "NA"

def getReceiptInfo(filename):
    contentFound = ""
    reader = easyocr.Reader(['en', 'de', 'fr'])
    result = reader.readtext(filename)
    for detection in result:
        contentFound += detection[1]
        contentFound += " "

    print(contentFound)

    title = extract_title(contentFound)
    date = extract_date(contentFound)
    total = extract_total(contentFound)
    phone_number = extract_phone_numbers(contentFound)

    extractedData = []
    extractedData.append(title)
    extractedData.append(date)
    extractedData.append(total)
    extractedData.append(phone_number)

    return extractedData

def generate_standard_receipt():
	buffer = BytesIO()
	p = canvas.Canvas(buffer)

	# Create a PDF document
	# p.drawString(100, 750, "Receipt")

	y = 700
	for book in user_data:
		p.drawString(100, y, f"Title: {book['title']}")
		p.drawString(100, y - 20, f"Author: {book['author']}")
		p.drawString(100, y - 40, f"Year: {book['publication_year']}")
		y -= 60

	p.showPage()
	p.save()

	buffer.seek(0)
	return buffer

@ocrFunc.route("/scanning", methods=['GET','POST'])
def scanning():
    filename = request.args.get('file_path')
    extension = os.path.splitext(filename)[1]

    if extension not in ALLOWED_EXTENSIONS:
        flash('File type not allowed. Please upload a file with one of the following extensions: {}'.format(", ".join(ALLOWED_EXTENSIONS)))
        return redirect(url_for("views.dashboard"))

    # language = langid.classify(contentFound) // contentFound is a list now, FIX THIS
    # if(language == 'en'):
    # else:
        # translatedData = translateData(contentFound)
        # processData(translatedData)    
        
    # print("Detected language:", language)
    extractedData = getReceiptInfo(filename)
    if request.method == "POST":
        contents = request.form.get('contents')
        purpose = request.form.get('purpose')
        newReceipt = receiptContents(Title = extractedData[0], Date = extractedData[1], Total = extractedData[2] ,PhoneNO = extractedData[3] ,Contents = contents, Purpose = purpose)
        db.session.add(newReceipt)
        db.session.commit()
        pdf_file = generate_standard_receipt()
        return send_file(pdf_file, as_attachment=True, download_name='book_catalog.pdf')

        return redirect(url_for("views.dashboard"))
    return render_template("ocrFunctions.html", extractedData=extractedData)