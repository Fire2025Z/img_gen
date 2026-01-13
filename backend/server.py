from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import re

app = FastAPI(title="AI Image Generator API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your Gemini API Key
GEMINI_API_KEY = "AIzaSyDt1frcEs72TNrmQkCyKe6PxKhI7Jm6TT4"

class GenerateRequest(BaseModel):
    prompt: str

def detect_language(text: str) -> str:
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
    if arabic_pattern.search(text):
        arabic_words = ['ال', 'في', 'من', 'على', 'أن', 'هذا', 'هذه']
        kurdish_words = ['هه‌موو', 'كه‌', 'بۆ', 'له‌', 'ئه‌م', 'ئه‌و', 'وه‌ك']
        arabic_count = sum(1 for word in arabic_words if word in text)
        kurdish_count = sum(1 for word in kurdish_words if word in text)
        return 'ku' if kurdish_count > arabic_count else 'ar'
    return 'en'

def validate_prompt(prompt: str) -> bool:
    try:
        return detect_language(prompt) in ['en', 'ar', 'ku']
    except:
        return False

@app.get("/")
async def root():
    return {"status": "Backend running on Railway"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Image Generator API"}

@app.post("/generate")
async def generate_image(request: GenerateRequest):
    if not validate_prompt(request.prompt):
        raise HTTPException(
            status_code=400,
            detail="Prompt must be in English, Arabic, or Kurdish only"
        )

    # Placeholder image: 1x1 white PNG encoded in Base64
    placeholder_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
    )

    return {
        "prompt": request.prompt,
        "image": placeholder_base64
    }
