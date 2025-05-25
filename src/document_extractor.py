import docx2txt
import pdfplumber
import os

def extract_text(file_path):
    if file_path.endswith('.docx'):
        return docx2txt.process(file_path)
    elif file_path.endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            return ''.join([page.extract_text() for page in pdf.pages])
    else:
        raise ValueError("Unsupported file type")

def save_text(text, output_file="output.txt"):
    with open(output_file, "w") as f:
        f.write(text)
