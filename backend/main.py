from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import base64
from pydantic import BaseModel
from PIL import Image, ImageDraw
import io
import requests

app = FastAPI()

# Allow Flutter app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return {"message": "AI Image Generator API", "status": "ready"}

@app.post("/generate")
async def generate_image(request: PromptRequest):
    print(f"Generating image for: {request.prompt}")
    
    try:
        # Try to generate with free API
        image_bytes = await generate_real_image(request.prompt)
        return {"image": base64.b64encode(image_bytes).decode()}
        
    except Exception as e:
        print(f"API error: {e}")
        # Create fallback image
        return create_fallback_image(request.prompt)

async def generate_real_image(prompt: str):
    """Generate real AI image using free API"""
    try:
        # Use Prodia API (free, no key needed)
        import asyncio
        
        # Create job
        url = "https://api.prodia.com/v1/sd/generate"
        response = requests.post(url, json={
            "prompt": prompt,
            "model": "dreamshaper_8_93211.safetensors [b5c85b7cce]",
            "negative_prompt": "",
            "steps": 25,
            "cfg_scale": 7,
            "seed": -1,
            "width": 512,
            "height": 512
        })
        
        if response.status_code == 200:
            job_id = response.json()["job"]
            
            # Check job status
            for _ in range(30):  # Max 30 seconds wait
                status_url = f"https://api.prodia.com/v1/job/{job_id}"
                status_resp = requests.get(status_url)
                
                if status_resp.status_code == 200:
                    data = status_resp.json()
                    if data["status"] == "succeeded":
                        # Get the image
                        image_url = data["imageUrl"]
                        img_response = requests.get(image_url)
                        return img_response.content
                    elif data["status"] == "failed":
                        break
                
                await asyncio.sleep(1)  # Wait 1 second between checks
            
    except Exception as e:
        print(f"Prodia error: {e}")
    
    # If Prodia fails, try another free API
    return generate_with_fallback_api(prompt)

def generate_with_fallback_api(prompt: str):
    """Try another free API"""
    try:
        # Use Pollinations API (completely free, no key)
        url = f"https://image.pollinations.ai/prompt/{prompt}"
        response = requests.get(url, params={
            "width": 512,
            "height": 512,
            "nologo": "true"
        })
        
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"Pollinations error: {e}")
    
    # If all APIs fail, create our own image
    return create_simple_image(prompt)

def create_simple_image(prompt: str):
    """Create a simple colored image with text"""
    # Create image with different colors based on prompt
    colors = {
        'red': (255, 0, 0),
        'blue': (0, 0, 255),
        'green': (0, 255, 0),
        'yellow': (255, 255, 0),
        'purple': (128, 0, 128),
        'orange': (255, 165, 0),
    }
    
    # Pick color based on prompt words
    bg_color = colors['blue']  # default
    
    for color_name, color_rgb in colors.items():
        if color_name in prompt.lower():
            bg_color = color_rgb
            break
    
    # Create image
    img = Image.new('RGB', (512, 512), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Add text
    draw.text((50, 50), "AI Generated", fill="white")
    draw.text((50, 100), f"Prompt: {prompt[:30]}...", fill="white")
    
    # Detect language
    if any(c in prompt for c in ['چ', 'پ', 'ژ', 'گ', 'ڕ', 'ڤ', 'ێ', 'ە']):
        lang = "Kurdish"
    elif any(ord(c) in range(0x0600, 0x06FF) for c in prompt):
        lang = "Arabic"
    else:
        lang = "English"
    
    draw.text((50, 150), f"Language: {lang}", fill="yellow")
    
    # Add some shapes
    draw.rectangle([100, 200, 300, 300], fill="white", outline="black", width=2)
    draw.ellipse([150, 350, 250, 450], fill="red", outline="black", width=2)
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def create_fallback_image(prompt: str):
    """Fallback JSON response"""
    image_bytes = create_simple_image(prompt)
    return {"image": base64.b64encode(image_bytes).decode()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)