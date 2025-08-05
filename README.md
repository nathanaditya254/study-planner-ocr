# Study Planner App 🧠⏰

A Flask-based web application to manage study tasks with automatic scheduling, break tracking, and OCR-based task entry from handwritten notes.

## Features
- Add tasks with deadlines and durations
- Auto-generate study schedules
- Track breaks
- Upload handwritten task images (OCR + GPT-4o)

## Tech Stack
- Python Flask + JavaScript
- Google Vision OCR
- OpenAI GPT-4o
- HTML/CSS

## Usage
1. `pip install -r requirements.txt`
2. Add `.env` with OpenAI and Google Vision keys
3. Run: `python app.py`

## OCR Setup
Make sure to include your `.json` Google credentials and `.env` file (not committed).

Flask
flask-cors
python-dotenv
google-cloud-vision
openai