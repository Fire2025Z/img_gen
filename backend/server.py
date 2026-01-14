# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import base64
# import uvicorn

# app = FastAPI(title="AI Image Generator")

# # Enable CORS - IMPORTANT for Flutter
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )

# class PromptRequest(BaseModel):
#     prompt: str

# @app.get("/")
# async def root():
#     return {"message": "AI Image Generator API is running!"}

# @app.get("/health")
# async def health():
#     return {"status": "healthy", "service": "AI Image Generator"}

# @app.post("/generate")
# async def generate_image(request: PromptRequest):
#     """Generate a simple image from text"""
    
#     # Create a colorful SVG image based on prompt
#     colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]
#     color = colors[hash(request.prompt) % len(colors)]
    
#     svg_content = f'''<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
#         <defs>
#             <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
#                 <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
#                 <stop offset="100%" style="stop-color:#2d2d2d;stop-opacity:1" />
#             </linearGradient>
#             <radialGradient id="grad2" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
#                 <stop offset="0%" style="stop-color:{color};stop-opacity:0.8" />
#                 <stop offset="100%" style="stop-color:{color}40;stop-opacity:0.3" />
#             </radialGradient>
#         </defs>
        
#         <rect width="100%" height="100%" fill="url(#grad1)"/>
        
#         <circle cx="200" cy="200" r="150" fill="url(#grad2)" opacity="0.7"/>
        
#         <rect x="50" y="150" width="300" height="100" rx="10" fill="rgba(0,0,0,0.5)"/>
        
#         <text x="200" y="180" font-family="Arial" font-size="16" fill="white" 
#               text-anchor="middle" font-weight="bold">AI Generated Image</text>
        
#         <text x="200" y="210" font-family="Arial" font-size="14" fill="{color}" 
#               text-anchor="middle">{request.prompt[:40]}</text>
        
#         <text x="200" y="350" font-family="Arial" font-size="12" fill="#888" 
#               text-anchor="middle">Powered by AI Image Generator</text>
#     </svg>'''
    
#     # Convert to base64
#     image_base64 = base64.b64encode(svg_content.encode()).decode()
    
#     return {
#         "success": True,
#         "image": image_base64,
#         "prompt": request.prompt,
#         "message": "Image generated successfully"
#     }

# if __name__ == "__main__":
#     print("=" * 50)
#     print("🚀 AI Image Generator Backend Server")
#     print("=" * 50)
#     print("📍 Local: http://localhost:8000")
#     print("📍 Network: http://<your-ip>:8000")
#     print("=" * 50)
#     print("📋 Endpoints:")
#     print("  GET  /         - API info")
#     print("  GET  /health   - Health check")
#     print("  POST /generate - Generate image")
#     print("=" * 50)
#     print("💡 Test with: curl -X POST http://localhost:8000/generate")
#     print('        -H "Content-Type: application/json"')
#     print('        -d \'{"prompt":"hello world"}\'')
#     print("=" * 50)
    
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import uvicorn
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json

app = FastAPI()

# CORS settings - CRITICAL for PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for PWA
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Specify methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
)

class PromptRequest(BaseModel):
    prompt: str

def create_png_image(prompt: str) -> bytes:
    """Create a PNG image instead of SVG for better PWA compatibility"""
    # Create a new image with a dark background
    width, height = 512, 512
    image = Image.new('RGB', (width, height), color=(26, 26, 26))
    draw = ImageDraw.Draw(image)
    
    try:
        # Try to load a font (use default if not available)
        font_large = ImageFont.truetype("arial.ttf", 32)
        font_medium = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        # Use default font if arial is not available
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw a decorative rectangle
    draw.rectangle([50, 100, width-50, height-100], 
                   outline=(207, 139, 252), width=3)
    
    # Draw title
    draw.text((width//2, 150), "AI Generated Image", 
              fill=(207, 139, 252), font=font_large, anchor="mm")
    
    # Draw the prompt text (wrapped)
    words = prompt.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        # Simple line wrapping
        if len(test_line) > 40:
            lines.append(' '.join(current_line[:-1]))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw each line
    y_position = 200
    for i, line in enumerate(lines[:3]):  # Max 3 lines
        draw.text((width//2, y_position + i*40), line, 
                  fill=(255, 255, 255), font=font_medium, anchor="mm")
    
    # Draw footer
    draw.text((width//2, height - 80), "Generated with AI", 
              fill=(136, 136, 136), font=font_small, anchor="mm")
    
    # Draw decorative circles
    draw.ellipse([100, 350, 150, 400], outline=(207, 139, 252), width=2)
    draw.ellipse([width-150, 350, width-100, 400], outline=(207, 139, 252), width=2)
    
    # Save image to bytes
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

@app.get("/")
def root():
    return {"message": "AI Image Generator API is running!"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "AI Image Generator"}

@app.post("/generate")
def generate_image(request: PromptRequest):
    print(f"PWA: Received prompt: {request.prompt}")
    
    try:
        # Create PNG image (better for PWA than SVG)
        png_bytes = create_png_image(request.prompt)
        
        # Convert to base64
        image_base64 = base64.b64encode(png_bytes).decode('utf-8')
        
        return {
            "success": True,
            "image": image_base64,
            "prompt": request.prompt,
            "message": "PNG image generated successfully",
            "format": "png"
        }
        
    except Exception as e:
        print(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add OPTIONS handler for CORS preflight
@app.options("/generate")
async def options_generate():
    return {"message": "CORS preflight"}

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 AI Image Generator Backend (PWA Compatible)")
    print("=" * 60)
    print("📍 PWA URL: http://localhost:8000")
    print("📍 Browser: Open http://localhost:8000 in browser")
    print("=" * 60)
    print("📋 Endpoints:")
    print("  GET  /         - API info")
    print("  GET  /health   - Health check")
    print("  POST /generate - Generate PNG image")
    print("=" * 60)
    print("⚠️  Note: Backend generates PNG for better PWA compatibility")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")