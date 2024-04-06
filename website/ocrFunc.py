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
from flask import Blueprint, render_template, request, redirect, send_file, url_for, flash, current_app as app, session
import spacy
from spacy.matcher import Matcher
from datetime import datetime
from sqlalchemy import desc
from langdetect import detect
from translate import Translator
from googletrans import Translator

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
    date_pattern = re.compile(r'\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:\d{1,2}[-/.])?\d{1,2}[-/.]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-\s]\d{1,2}(?:st|nd|rd|th)?(?:,\s+\d{2,4})?|\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b(?:day)?(?:,?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))?(?:\s+\d{2,4})?|\d{1,2}:\d{2}\s*(?:a.m.|p.m.)?|\d{1,2}(?:\.\d{2})?\s*(?:a.m.|p.m.|hours)?|(?:\d{1,2}(?:\s*(?:a.m.|p.m.|hours))?|midnight|noon)(?:\s+(?:at\s+)?(?:\d{1,2}:\d{2})?(?:\s*(?:a.m.|p.m.))?)?)\b')

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
    total_index = contentFound.find('Total')
    if total_index != -1:
        total_match = re.search(r'\d+\.\d+', contentFound[total_index:])
        if total_match:
            total_value = total_match.group()
            print("Next Value after 'Total':", total_value)
            return total_value
        else:
            return "NA"    

def extract_items_and_prices(content):
    item_name_pattern = re.compile(r'\((\d+)\)\s*(.*?)\s*-\s*(\d+)')
    matches = item_name_pattern.findall(content)
    item_names = [match[1].strip() for match in matches]
    prices = [int(match[2]) for match in matches]
    return item_names, prices


def getReceiptInfo(filename):
    contentFound = ""
    contentFoundList = []
    reader = easyocr.Reader(['en', 'de', 'fr'])
    result = reader.readtext(filename)
    for detection in result:
        contentFoundList.append(detection[1])
        # contentFound += " "

    # print(contentFoundList)

    # language = detect(contentFoundList)

    # print(language)

    translator = Translator()
    translated_list = [translator.translate(text, dest='en').text for text in contentFoundList]
    contentFound = " ".join(translated_list)


    # print(contentFound)

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

@ocrFunc.route("/scanning", methods=['GET','POST'])
def scanning():
    filename = request.args.get('file_path')
    extension = os.path.splitext(filename)[1]

    if extension not in ALLOWED_EXTENSIONS:
        flash('File type not allowed. Please upload a file with one of the following extensions: {}'.format(", ".join(ALLOWED_EXTENSIONS)))
        return redirect(url_for("views.dashboard"))

    extractedData = getReceiptInfo(filename)
    
        # translatedData = translateData(contentFound)
        # processData(translatedData)    
        
    # print("Detected language:", language)

    last_receipt = receiptContents.query.order_by(desc(receiptContents.RecieptNo)).first()
    current_receipt_no = last_receipt.RecieptNo if last_receipt else 0
    current_receipt_no += 1
    print(current_receipt_no)
    if request.method == "POST":
        email = session.get('user-id')
        contents = request.form.get('contents')
        item_names, prices = extract_items_and_prices(contents)
        purpose = request.form.get('purpose')

        Title = request.form.get('title')
        Date = request.form.get('date')
        Total = request.form.get('total')
        Phone = request.form.get('phoneno')

        # uploads/email/std/os.file.save

        newReceipt = receiptContents(Title = Title, Email= email, Date = Date, Total = Total ,PhoneNO = Phone ,Contents = contents, Purpose = purpose)
        db.session.add(newReceipt)
        db.session.commit()

        # filename = "Receipt-"+str(current_receipt_no)+".pdf"
        # # option = {
        # #     "enable-local-file-access": ""
        # # }
        
        # html = render_template(
        # "templates/stdReceipt.html")
        # pdf = pdfkit.from_string(html, False)
        # response = make_response(pdf)
        # response.headers["Content-Type"] = "application/pdf"
        # response.headers["Content-Disposition"] = f"inline; filename={filename}"
        # return response


        # fileName = secure_filename(filename)
        # newPath = os.path.join(app.config['UPLOAD_FOLDER'], email)
        # newPath = os.path.join(newPath, 'std')
        # if not os.path.exists(newPath):
        #     os.makedirs(newPath)
        # fileName.save(os.path.join(newPath, fileName))

        # pdf_file = generate_standard_receipt()
        # return send_file(pdf_file, as_attachment=True, download_name='book_catalog.pdf')

        generate_and_save_pdf(current_receipt_no, email, Title, Date, Total, Phone, item_names, prices)
        return redirect(url_for("views.dashboard"))
    
    return render_template("ocrFunctions.html", extractedData=extractedData, no = current_receipt_no)