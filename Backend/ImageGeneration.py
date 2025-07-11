import requests
import asyncio
from random import randint
from PIL import Image
import requests
import os
from time import sleep
from dotenv import load_dotenv

# Load API Key from .env
load_dotenv()
API_KEY = os.getenv("HuggingFaceAPIKey")

# API URL and Headers
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Directory for saving images
IMAGE_DIR = "Data"
os.makedirs(IMAGE_DIR, exist_ok=True)

def open_images(prompt):
    """Opens generated images from the Data folder."""
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    
    for file in files:
        image_path = os.path.join(IMAGE_DIR, file)
        try:
            img = Image.open(image_path)
            print(f"✅ Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"❌ Unable to open {image_path} (file may be missing)")

async def query(payload):
    """Sends a request to the Hugging Face API and returns the response."""
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return response.content
        else:
            print(f"⚠️ API Error: {response.status_code} - {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

async def generate_images(prompt: str, quality: str = "4K"):

    """Generates images using the Hugging Face API."""
    tasks = []
    for i in range(4):
        payload = {
            "inputs": f"{prompt}, quality={quality}, sharpness maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",

        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
    
    # Wait for all API responses
    image_bytes_list = await asyncio.gather(*tasks)
    
    # Check if image_bytes_list contains valid data
    if not all(image_bytes_list):
        print("❌ Error: One or more images were not generated successfully.")
        return

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            file_path = os.path.join(IMAGE_DIR, f"{prompt.replace(' ', '_')}{i + 1}.jpg")
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            if image_bytes:
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                print(f"✅ Image saved: {file_path}")

        else:
            print(f"❌ Error: API did not return a valid image for {IMAGE_DIR}/{prompt.replace(' ', '_')}{i + 1}.jpg")

def GenerateImages(prompt: str):
    """Runs the image generation process."""
    print("🚀 Generating Images...")
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Main loop to monitor the input file
while True:
    try:
        with open("Frontend/Files/ImageGeneration.data", "r") as f:
            data = f.read()
        
        # Extract prompt and status
        prompt, status = data.split(",")
        
        if status.strip().lower() == "true":
            GenerateImages(prompt=prompt.strip())
            
            # Update status file
            with open("Frontend/Files/ImageGeneration.data", "w") as f:
                f.write("False, False")
            break
        else:
            sleep(1)
    except Exception as e:
        print(f"⚠️ Error: {e}")
        sleep(1)
