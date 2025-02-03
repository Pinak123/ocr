from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import cv2
from PIL import Image
import json
import pytesseract

app = FastAPI()
def perform_ocr(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

import google.generativeai as genai

genai.configure(api_key='AIzaSyBOP8mUuxScMA7GX6aTube9uvgHsZJzcCs')

def extract_invoice_info(text):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Extract the following information from this invoice text: invoice number, date, total amount, and line items. Format the output as JSON.\n\nInvoice text:\n{text}"
    response = model.generate_content(prompt)
    return response.text



def display_results(items):
    print("\nExtracted Invoice Items:")
    print("-------------------------")
    for item in items:
        print(f"Product: {item['product_name']}")
        print(f"Quantity: {item['quantity']}")
        print(f"Price: ${item['price']}")
        print("-------------------------")



# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def root():
    return {"message": "Welcome to the Invoice OCR Service!"}
