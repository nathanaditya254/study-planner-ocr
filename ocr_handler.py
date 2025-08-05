import json
import os
from google.cloud import vision
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not GOOGLE_APPLICATION_CREDENTIALS:
    raise EnvironmentError("Missing GOOGLE_APPLICATION_CREDENTIALS in .env")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

key = os.getenv("OPENAI_API_KEY")
if not key:
    raise EnvironmentError("Missing OPENAI_API_KEY in .env")

client = OpenAI(api_key=key)

def extract_and_parse(image_path):
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()

    image = vision.Image(content=image_bytes)
    vision_client = vision.ImageAnnotatorClient()
    response = vision_client.document_text_detection(image=image)

    texts = response.text_annotations
    if not texts:
        return {"error": "No text detected in image."}

    ocr_text = texts[0].description.strip()
    print("OCR OUTPUT:\n", ocr_text)  # to catch errors

    prompt = f"""
You are an intelligent data extractor. Given the OCR-parsed handwritten task below, extract the following:
- name: task name or description
- due_date: when the task is due (guess if needed) in ISO format (YYYY-MM-DDTHH:MM)
- duration: how long it will take in minutes (estimate if unclear)
- type: category like homework, test, project, etc.

Respond only with a valid JSON object, without markdown or code blocks.

Parsed Text:
{ocr_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
