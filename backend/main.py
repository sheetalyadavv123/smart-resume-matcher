from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import fitz  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "AI Resume Matcher API is running!"}

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    # Read the uploaded PDF file
    data = await file.read()
    
    # Open the PDF with PyMuPDF
    doc = fitz.open(stream=data, filetype="pdf")
    full_text = ""
    
    for page in doc:
        full_text += page.get_text()
        
    return {
        "filename": file.filename,
        "text_content": full_text[:500] + "..."  # Returning first 500 chars to test
    }