# ==========================================
# RESUME SKILL EXTRACTOR
# MAIN APPLICATION
# ==========================================


# ------------------------------------------
# Import required libraries
# ------------------------------------------

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse
import pdfplumber

from docx import Document

import os

import uuid


# Import our skill extraction function

from skill_extractor import extract_skills, categorize_skills, calculate_skill_match


# ------------------------------------------
# Create FastAPI application
# ------------------------------------------

app = FastAPI(

    title="Resume Skill Extractor",

    description="Upload a resume and extract skills",

    version="1.0"
)


# ------------------------------------------
# Upload folder
# ------------------------------------------

UPLOAD_FOLDER = "uploads"


# Create uploads folder automatically
# if it doesn't already exist

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ==========================================
# FUNCTION 1
# Extract text from PDF
# ==========================================

def extract_text_from_pdf(file_path):

    # Variable to store extracted text

    text = ""


    # Open PDF

    with pdfplumber.open(file_path) as pdf:


        # Read every page

        for page in pdf.pages:


            # Extract text from current page

            page_text = page.extract_text()


            # If text exists

            if page_text:

                text += page_text + "\n"


    # Return complete resume text

    return text


# ==========================================
# FUNCTION 2
# Extract text from DOCX
# ==========================================

def extract_text_from_docx(file_path):

    # Open Word document

    document = Document(file_path)


    # Variable to store text

    text = ""


    # Read every paragraph

    for paragraph in document.paragraphs:

        text += paragraph.text + "\n"


    # Return complete text

    return text


# ==========================================
# API ENDPOINT
# Home page
# ==========================================

@app.get("/", response_class=HTMLResponse)
def home():

    with open(
        "templates/index.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ==========================================
# API ENDPOINT
# Upload Resume
# ==========================================

@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):

    # Check whether a file was selected
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    # Allowed file types
    allowed_extensions = [
        ".pdf",
        ".docx"
    ]

    # Get file extension
    file_extension = os.path.splitext(
        file.filename
    )[1].lower()

    # Check file type
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    # Create unique filename
    unique_filename = (
        str(uuid.uuid4())
        + file_extension
    )

    # Create complete file path
    file_path = os.path.join(
        UPLOAD_FOLDER,
        unique_filename
    )

    # Read uploaded file
    contents = await file.read()

    # Save uploaded file
    with open(
        file_path,
        "wb"
    ) as output_file:
        output_file.write(contents)

    # Extract text from resume
    try:

        if file_extension == ".pdf":

            resume_text = extract_text_from_pdf(
                file_path
            )

        else:

            resume_text = extract_text_from_docx(
                file_path
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Could not read resume: {str(error)}"
        )

    # Check whether text was extracted
    if not resume_text.strip():

        raise HTTPException(
            status_code=400,
            detail="Could not extract text from the resume."
        )

    # Extract skills from resume
    skills = extract_skills(
        resume_text
    )

    # Categorize extracted skills
    categorized_skills = categorize_skills(
        skills
    )

    # Extract skills from Job Description
    job_skills = extract_skills(
        job_description
    )

    # Calculate skill match
    match_result = calculate_skill_match(
        skills,
        job_skills
    )

    # Return result
    return {
        "filename": file.filename,
        "skills": skills,
        "skill_count": len(skills),
        "categories": categorized_skills,
        "job_skills": job_skills,
        "match_percentage": match_result["match_percentage"],
        "matched_skills": match_result["matched_skills"],
        "missing_skills": match_result["missing_skills"],
        "text": resume_text
    }