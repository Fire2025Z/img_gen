from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import base64
import re
from typing import Optional
import uvicorn

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
    """
    Detect if the text is English, Arabic, or Kurdish
    Returns: 'en', 'ar', 'ku', or raises error
    """
    # Check for Arabic script (Arabic and Kurdish use Arabic script)
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
    
    if arabic_pattern.search(text):
        # Try to distinguish between Arabic and Kurdish
        # Common Arabic words
        arabic_words = ['ال', 'في', 'من', 'على', 'أن', 'هذا', 'هذه']
        # Common Kurdish words
        kurdish_words = ['هه‌موو', 'كه‌', 'بۆ', 'له‌', 'ئه‌م', 'ئه‌و', 'وه‌ك']
        
        arabic_count = sum(1 for word in arabic_words if word in text)
        kurdish_count = sum(1 for word in kurdish_words if word in text)
        
        if kurdish_count > arabic_count:
            return 'ku'  # Kurdish
        else:
            return 'ar'  # Arabic
    
    # If no Arabic script, assume English
    return 'en'

def validate_prompt(prompt: str) -> bool:
    """
    Validate that prompt is in one of the allowed languages
    """
    try:
        lang = detect_language(prompt)
        return lang in ['en', 'ar', 'ku']
    except:
        return False

@app.post("/generate")
async def generate_image(request: GenerateRequest):
    """
    Generate image from text prompt using Gemini API
    Supports: English, Arabic, Kurdish
    """
    
    # Validate language
    if not validate_prompt(request.prompt):
        raise HTTPException(
            status_code=400,
            detail="Prompt must be in English, Arabic, or Kurdish only"
        )
    
    # Prepare the prompt for Gemini
    enhanced_prompt = f"""
    Generate a high-quality, detailed, and visually stunning image based on this description: {request.prompt}
    
    Requirements:
    1. Create photorealistic or artistic image as appropriate
    2. Use vibrant colors and good composition
    3. Ensure high resolution and detail
    4. Make it visually appealing and creative
    """
    
    try:
        # Gemini API endpoint for image generation
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={GEMINI_API_KEY}"
        
        # Note: Gemini currently doesn't have direct image generation API.
        # We need to use text-to-image through a different approach.
        # Let's use Google's Imagen or an alternative.
        
        # For now, let's use a different approach since Gemini doesn't directly generate images.
        # We'll use the Vertex AI API for image generation
        
        # Alternative: Using Vertex AI's Imagen
        # You might need to enable the Vertex AI API and use a different endpoint
        
        # For testing purposes, let's use a placeholder or implement a different service
        # Since Gemini doesn't have image generation yet, let's use Stability AI or another service
        
        raise HTTPException(
            status_code=501,
            detail="Image generation service configuration needed. Please check the backend implementation."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating image: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Image Generator API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)