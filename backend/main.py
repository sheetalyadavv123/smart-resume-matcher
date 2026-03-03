from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import os
import json
from google import genai
from dotenv import load_dotenv

# 1. Load the .env file
load_dotenv()

app = FastAPI()

# 2. Setup CORS so React can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# It will look for key in the .env file
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.get("/")
def home():
    return {"message": "AI Resume Matcher API is running!"}

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...), jd: str = Form(...)):
    # 4. Extract text from the uploaded PDF
    pdf_data = await file.read()
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    resume_text = ""
    for page in doc:
        resume_text += page.get_text()

    # 5. Create the prompt
    prompt = f"""
    You are an expert ATS (Applicant Tracking System). 
    Compare the Resume below with the Job Description (JD).
    
    Resume: {resume_text}
    JD: {jd}
    
    Provide the result in strictly JSON format with these keys:
    - match_percentage (number)
    - missing_keywords (list of strings)
    - improvement_tips (list of strings)
    """

    
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt
    )
    
    
    clean_json = response.text.replace("```json", "").replace("```", "").strip()
    
    return json.loads(clean_json)