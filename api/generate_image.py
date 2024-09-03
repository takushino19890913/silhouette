import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

def generate_image(prompt):
    api_url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
    api_key = os.getenv('STABILITY_API_KEY')

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "text_prompts": [
            {
                "text": f"{prompt} with a white background",
                "weight": 1.0
            }
        ],
        "cfg_scale": 7.0,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 50
    }

    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        response_json = response.json()
        artifacts = response_json.get("artifacts", [])
        if artifacts:
            artifact = artifacts[0]
            if artifact.get("finishReason") == "SUCCESS":
                img_data = artifact.get("base64")
                return base64.b64decode(img_data)
    return None