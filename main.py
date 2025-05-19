import os
import requests
import time
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

subscription_key = os.getenv("subscription_key")
endpoint = os.getenv("endpoint")

ocr_url = endpoint + "/vision/v3.2/read/analyze"
pdf_path = "handwritten.pdf"

# Read PDF as binary
with open(pdf_path, "rb") as pdf_file:
    pdf_data = pdf_file.read()

headers = {
    "Ocp-Apim-Subscription-Key": subscription_key,
    "Content-Type": "application/pdf"
}

# Send PDF to Azure OCR
response = requests.post(ocr_url, headers=headers, data=pdf_data)
operation_url = response.headers["Operation-Location"]

# Poll for result
while True:
    result = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": subscription_key})
    analysis = result.json()
    
    if "analyzeResult" in analysis:
        break
    elif "status" in analysis and analysis["status"] == "failed":
        print("Analysis failed.")
        exit(1)
    time.sleep(1)

# Collect all extracted text
extracted_text = ""
for read_result in analysis["analyzeResult"]["readResults"]:
    for line in read_result["lines"]:
        extracted_text += line["text"] + "\n"

# Create a new PDF and add the extracted text
pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=10)
pdf.set_font("Arial", size=22)

# Split text into lines and add them to PDF
pdf.multi_cell(0, 15, extracted_text)

# Save the new PDF file
output_pdf_path = "extracted_text_output.pdf"
pdf.output(output_pdf_path)
print(f"Extracted text PDF created: {output_pdf_path}")