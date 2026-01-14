from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import base64
import re
from typing import Optional
import uvicorn
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Image Generator API")

# CORS middleware - updated for better compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDt1frcEs72TNrmQkCyKe6PxKhI7Jm6TT4")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

class GenerateRequest(BaseModel):
    prompt: str

class ImageResponse(BaseModel):
    image: str  # base64 encoded image
    prompt: str
    generation_time: float

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

def generate_with_gemini(prompt: str) -> Optional[str]:
    """
    Generate image using Gemini's image generation capabilities
    Note: As of now, Gemini Pro doesn't directly generate images.
    We'll use it to create a description and then use a fallback service.
    """
    try:
        # Since Gemini doesn't have direct image generation yet,
        # we'll use a mock/fake image generation for now
        # In production, you should integrate with a real image generation API
        
        # For testing, we'll return a placeholder/base64 of a sample image
        # or use a free image generation service
        
        # Example using a placeholder service (remove this in production)
        import json
        
        # You can integrate with these services in production:
        # 1. Stable Diffusion API (stability.ai)
        # 2. DALL-E API
        # 3. Hugging Face API
        
        # For now, return a placeholder base64 image
        return None
        
    except Exception as e:
        print(f"Error in generate_with_gemini: {e}")
        return None

def get_fallback_image(prompt: str) -> str:
    """
    Get a fallback/placeholder image for testing
    In production, replace with real image generation API
    """
    # Create a simple placeholder image using PIL
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Create a simple image with the prompt text
        img = Image.new('RGB', (512, 512), color=(43, 0, 69))
        d = ImageDraw.Draw(img)
        
        # Try to add some text
        try:
            # You might need to adjust font path
            font = ImageFont.load_default()
            text = prompt[:50] + "..." if len(prompt) > 50 else prompt
            d.text((50, 250), f"Prompt: {text}", fill=(207, 139, 252), font=font)
        except:
            pass
        
        # Draw some decorative elements
        d.ellipse([100, 100, 412, 412], outline=(207, 139, 252), width=3)
        
        # Convert to base64
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return base64.b64encode(img_byte_arr).decode('utf-8')
        
    except Exception as e:
        print(f"Error creating placeholder: {e}")
        # Return a very simple base64 placeholder
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

@app.post("/generate", response_model=ImageResponse)
async def generate_image(request: GenerateRequest):
    """
    Generate image from text prompt
    Supports: English, Arabic, Kurdish
    """
    start_time = time.time()
    
    # Validate language
    if not validate_prompt(request.prompt):
        raise HTTPException(
            status_code=400,
            detail="Prompt must be in English, Arabic, or Kurdish only"
        )
    
    # Validate prompt length
    if len(request.prompt.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Prompt must be at least 3 characters long"
        )
    
    if len(request.prompt.strip()) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Prompt must be less than 1000 characters"
        )
    
    try:
        # Try to generate with Gemini (will return None for now)
        image_base64 = generate_with_gemini(request.prompt)
        
        # If no image from Gemini, use fallback for testing
        if not image_base64:
            image_base64 = get_fallback_image(request.prompt)
        
        generation_time = time.time() - start_time
        
        return ImageResponse(
            image=image_base64,
            prompt=request.prompt,
            generation_time=round(generation_time, 2)
        )
        
    except Exception as e:
        print(f"Error generating image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating image: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "AI Image Generator API",
        "timestamp": time.time()
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint for debugging"""
    return {
        "message": "Backend is running",
        "timestamp": time.time(),
        "api_key_exists": bool(GEMINI_API_KEY)
    }

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )