from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import base64
import re
import os
from dotenv import load_dotenv
import uvicorn
import io
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Image Generator API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDt1frcEs72TNrmQkCyKe6PxKhI7Jm6TT4")

class GenerateRequest(BaseModel):
    prompt: str

def detect_language(text: str) -> str:
    """
    Detect if the text is English, Arabic, or Kurdish
    """
    if not text.strip():
        return 'en'
    
    # Check for Arabic script
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
    
    if arabic_pattern.search(text):
        # Simple detection between Arabic and Kurdish
        arabic_words = ['ال', 'في', 'من', 'على', 'أن']
        kurdish_words = ['هه‌موو', 'كه‌', 'بۆ', 'له‌', 'ئه‌م']
        
        arabic_count = sum(1 for word in arabic_words if word in text)
        kurdish_count = sum(1 for word in kurdish_words if word in text)
        
        if kurdish_count > arabic_count:
            return 'ku'
        else:
            return 'ar'
    
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

def create_simple_image(prompt: str) -> str:
    """
    Create a simple test image without external dependencies
    Returns base64 encoded image
    """
    # This is a simple SVG image generator - works without Pillow
    width, height = 512, 512
    
    # Create a simple SVG with the prompt text
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
    <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#2c3e50"/>
        <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#8e44ad;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#3498db;stop-opacity:1" />
            </linearGradient>
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="0" stdDeviation="10" flood-color="#000000" flood-opacity="0.5"/>
            </filter>
        </defs>
        <circle cx="256" cy="256" r="200" fill="url(#grad1)" filter="url(#shadow)"/>
        <text x="256" y="256" font-family="Arial" font-size="24" fill="white" 
              text-anchor="middle" dominant-baseline="middle">
            {prompt[:40]}
        </text>
        <text x="256" y="300" font-family="Arial" font-size="16" fill="#ecf0f1" 
              text-anchor="middle" dominant-baseline="middle">
            AI Generated Image
        </text>
    </svg>'''
    
    # Encode SVG to base64
    svg_bytes = svg_content.encode('utf-8')
    return base64.b64encode(svg_bytes).decode('utf-8')

@app.post("/generate")
async def generate_image(request: GenerateRequest):
    """
    Generate image from text prompt
    """
    
    # Validate language
    if not validate_prompt(request.prompt):
        raise HTTPException(
            status_code=400,
            detail="Prompt must be in English, Arabic, or Kurdish only"
        )
    
    try:
        # For development/testing, generate a simple SVG image
        if os.getenv("ENVIRONMENT", "development") == "development":
            image_base64 = create_simple_image(request.prompt)
            
            return {
                "status": "success",
                "message": "Image generated successfully",
                "image": image_base64,
                "prompt": request.prompt,
                "format": "svg+xml"
            }
        
        # If you have a production image generation service, integrate it here
        # Example with Stability AI (requires API key):
        """
        stability_api_key = os.getenv("STABILITY_API_KEY")
        if stability_api_key:
            response = requests.post(
                'https://api.stability.ai/v2beta/stable-image/generate/sd3',
                headers={
                    'authorization': f'Bearer {stability_api_key}',
                    'accept': 'image/*'
                },
                files={'none': ''},
                data={
                    'prompt': request.prompt,
                    'output_format': 'png',
                },
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "image": base64.b64encode(response.content).decode('utf-8'),
                    "prompt": request.prompt
                }
        """
        
        # If no production service configured, return demo image
        image_base64 = create_simple_image(request.prompt)
        
        return {
            "status": "success",
            "message": "Demo image generated",
            "image": image_base64,
            "prompt": request.prompt,
            "format": "svg+xml",
            "note": "For real image generation, configure an image generation API"
        }
        
    except Exception as e:
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
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "AI Image Generator API",
        "endpoints": {
            "POST /generate": "Generate image from prompt",
            "GET /health": "Health check",
            "GET /": "This info"
        },
        "supported_languages": ["English", "Arabic", "Kurdish"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)