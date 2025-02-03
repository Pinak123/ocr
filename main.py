from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from pydantic import BaseModel
from typing import List
import cv2
from PIL import Image
import json
import pytesseract
import os
import shutil

import uvicorn
# pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = FastAPI()

if not os.path.exists("uploads"):
    os.makedirs("uploads")

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


@app.post("/uploadfile/" , response_class=ORJSONResponse)
async def create_upload_file(file: UploadFile = File(...)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    extracted_text = perform_ocr(file_location)
    invoice_data = extract_invoice_info(extracted_text)
    print(invoice_data)
    return JSONResponse(content=invoice_data, status_code=200)


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8000))
#     uvicorn.run("main:app", host="localhost", port=port, reload=False)