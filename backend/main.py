from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import fitz  
import os
import json
import re
from google import genai
from dotenv import load_dotenv

# Load .env first!
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug: Print if the API key is actually found (it won't show the full key for security)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file!")
else:
    print(f"✅ API Key loaded successfully (starts with: {api_key[:5]}...)")

# Initialize the client
client = genai.Client(api_key=api_key)

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...), jd: str = Form(...)):
    try:
        # 1. Extract Text
        print(f"Processing file: {file.filename}")
        pdf_data = await file.read()
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        resume_text = "".join([page.get_text() for page in doc])
        
        if not resume_text:
            return {"error": "Could not extract text from PDF. Is it an image?"}

        # 2. AI Prompt
        prompt = f"""
        Analyze this Resume against the Job Description. 
        Return ONLY a JSON object. No markdown, no 'json' word.
        Keys: "match_percentage", "missing_keywords", "improvement_tips"
        
        Resume: {resume_text}
        JD: {jd}
        """

        # 3. Call Gemini
        print("Sending to Gemini...")
        response = client.models.generate_content(
        model="gemini-1.5-flash-latest",
        contents=prompt
         )

        # 4. Clean and Parse JSON
        raw_text = response.text
        # Look for the JSON structure in the response
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        
        if json_match:
            return json.loads(json_match.group(0))
        else:
            print(f"AI Response was not JSON: {raw_text}")
            return {"error": "AI response formatting error"}

    except Exception as e:
        # THIS WILL PRINT THE ACTUAL ERROR IN YOUR TERMINAL
        print(f"🔥 CRITICAL ERROR: {str(e)}")
        return {"error": "Internal Server Error", "details": str(e)}