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
import spacy
from spacy.matcher import Matcher
from datetime import datetime


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

def extract_date(contentFound):
    date_pattern = re.compile(r'\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:\d{1,2}[-/])?\d{1,2}[-/]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-\s]\d{1,2}(?:st|nd|rd|th)?(?:,\s+\d{2,4})?|\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b(?:day)?(?:,?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))?(?:\s+\d{2,4})?|\d{1,2}:\d{2}\s*(?:a.m.|p.m.)?|\d{1,2}(?:\.\d{2})?\s*(?:a.m.|p.m.|hours)?|(?:\d{1,2}(?:\s*(?:a.m.|p.m.|hours))?|midnight|noon)(?:\s+(?:at\s+)?(?:\d{1,2}:\d{2})?(?:\s*(?:a.m.|p.m.))?)?)\b')

    date = ""
    matches = re.findall(date_pattern, contentFound)
    print("Date Found: ")
    for match in matches:
        if re.search(r'Date\s?' + re.escape(match), contentFound):
            print(match)
            return date
        else:
            return "NA"
            # break

def extract_phone_numbers(text):
    # Define the regular expression pattern to match Indian phone numbers
    pattern = r'\b(?:\d{5}[-.\s]??\d{5}|\d{10})\b'

    # Find all matches in the text
    phone_numbers = re.findall(pattern, text)

    return phone_numbers

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

def extract_title(contentFound):
    nlp = spacy.load("en_core_web_sm")
    about_doc = nlp(contentFound)
    matcher = Matcher(nlp.vocab)
    print("Printing Proper nouns")
    pattern = [{"POS": "PROPN"}]
    matcher.add("TITLE", [pattern])
    matches = matcher(about_doc)

    for _, start, end in matches:
        span = about_doc[start:end]
        print("TITLE: ")
        title = span.text
        return title
        # break


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
        contentFound += " "

    title = extract_title(contentFound)
    date = extract_date(contentFound)
    total = extract_total(contentFound)
    phone_number = extract_phone_numbers(contentFound)

    extractedData = []
    extractedData.append(title)
    extractedData.append(date)
    extractedData.append(total)
    extractedData.append(phone_number)

    language = langid.classify(contentFound)
    # print("Detected language:", language)
    return render_template("ocrFunctions.html", text=contentFound)
# title date total phone number content