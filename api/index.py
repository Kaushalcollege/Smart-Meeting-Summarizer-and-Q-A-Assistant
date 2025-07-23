# api/index.py

import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Hugging Face API Configuration ---
HF_API_URL = "https://api-inference.huggingface.co/models/"
HF_TOKEN = os.getenv("HF_TOKEN") # Get token from Vercel environment variables
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_api(payload, model_name):
    response = requests.post(HF_API_URL + model_name, headers=headers, json=payload)
    response.raise_for_status() # Raise an exception for bad status codes
    return response.json()

# --- Pydantic Models ---
class Transcript(BaseModel):
    text: str

class QA_Input(BaseModel):
    question: str
    context: str

# --- API Endpoints ---
@app.post("/summarize")
def summarize_the_transcript(transcript: Transcript):
    model_name = "philschmid/distilbart-cnn-12-6-samsum"
    payload = {"inputs": transcript.text}
    result = query_api(payload, model_name)
    return {"summary": result[0]['summary_text']}

@app.post("/ask")
def ask_question(qa_input: QA_Input):
    model_name = "kaushalcol/bart-dialogsum-finetuned"
    payload = {
        "inputs": {
            "question": qa_input.question,
            "context": qa_input.context
        }
    }
    result = query_api(payload, model_name)
    return {"answer": result['answer']}

@app.post("/actions")
def get_action_items(transcript: Transcript):
    model_name = "facebook/bart-large-mnli"
    payload = {
        "inputs": transcript.text.split('\n'), # Send sentences as a list
        "parameters": {"candidate_labels": ["action item", "commitment", "task", "general discussion"]}
    }
    results = query_api(payload, model_name)
    action_items = []
    for result in results:
        # Check if the sentence was classified as an action item with high confidence
        if result['labels'][0] != 'general discussion' and result['scores'][0] > 0.75:
            action_items.append(result['sequence'])

    return {"action_items": action_items}