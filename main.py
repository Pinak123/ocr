import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from pydantic import BaseModel
from typing import List
import cv2
from PIL import Image
import json
from pymongo import MongoClient
import pytesseract
import os
import shutil
from json_repair import repair_json
import uvicorn
# pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = FastAPI()

if not os.path.exists("uploads"):
    os.makedirs("uploads")

def perform_ocr(image_stream):
    image = Image.open(image_stream)
    text = pytesseract.image_to_string(image)
    return text

import google.generativeai as genai

genai.configure(api_key='AIzaSyBOP8mUuxScMA7GX6aTube9uvgHsZJzcCs')

def extract_invoice_info(text):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Extract the following information from this invoice text: invoice number, date, total amount, and line items. Format the output as JSON.\n\nInvoice text:\n{text}"
    response = model.generate_content(prompt)
    return response.text



# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mongo DB
@app.get('/')
def root():
    return {"message": "Welcome to the Invoice OCR Service!"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    
        # Process file upload
        image_stream = io.BytesIO(await file.read())
        
        # Perform OCR
        extracted_text = perform_ocr(image_stream)
        
        # Extract invoice data
        invoice_data = extract_invoice_info(extracted_text)
        repaired_json = repair_json(invoice_data)
        parsed_data = json.loads(repaired_json)
        print("Invoice data:", parsed_data)
        
        return   parsed_data
        
  

@app.get('/home')
def home():
    return {"message": "Welcome Home"}