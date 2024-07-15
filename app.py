from flask import Flask, request, render_template, jsonify
import pdfplumber
import re
import spacy
import os
import tempfile

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        if file:
            # Save the uploaded PDF file to a temporary directory
            pdf_path = save_uploaded_pdf(file)
            
            if pdf_path:
                # Extract information from the PDF
                name, emails, phone_numbers, skills, _ = extract_information_from_pdf(pdf_path)
                
                # Render result template with extracted information
                return render_template('upload.html', name=name, emails=emails, phone_numbers=phone_numbers, skills=skills)

            return jsonify({'error': 'Failed to process PDF'})

    # Render upload template by default
    return render_template('upload.html')

def save_uploaded_pdf(file):
    try:
        # Save the uploaded PDF file to a temporary directory
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, file.filename)
        file.save(pdf_path)
        return pdf_path
    except Exception as e:
        print("Error saving uploaded PDF:", e)
        return None

def extract_information_from_pdf(pdf_path):
    try:
        # Your provided code for extracting information from PDF resumes
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_regex = r'\b(?:\d{3}[-.]?|\(\d{3}\) ?)\d{3}[-.]?\d{4}\b'
        skills_list = ["Python", "Java", "JavaScript", "SQL", "Machine Learning", "Data Analysis"]
        skills_regex = r'\b(?:' + '|'.join(skills_list) + r')\b'

        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()

        name = text.split('\n')[0].strip()
        emails = re.findall(email_regex, text)
        phone_numbers = re.findall(phone_regex, text)
        skills = re.findall(skills_regex, text)

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

        return name, emails, phone_numbers, skills, names
    except Exception as e:
        print("Error extracting information from PDF:", e)
        return None, None, None, None, None

if __name__ == '__main__':
    app.run(debug=True)