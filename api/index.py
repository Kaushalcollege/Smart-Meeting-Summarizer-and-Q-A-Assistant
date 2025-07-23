# api/index.py

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- CORS Middleware ---
origins = ["*"] # Allow all origins for simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Lazy-loading Models ---
# We create placeholders. The models will only be loaded into memory
# when the corresponding endpoint is called for the first time.
models = {}

def get_summarizer():
    if "summarizer" not in models:
        models["summarizer"] = pipeline("summarization", model="philschmid/distilbart-cnn-12-6-samsum")
    return models["summarizer"]

def get_qa():
    if "qa" not in models:
        models["qa"] = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    return models["qa"]

def get_classifier():
    if "classifier" not in models:
        models["classifier"] = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    return models["classifier"]

# --- Pydantic Models ---
class Transcript(BaseModel):
    text: str

class QA_Input(BaseModel):
    question: str
    context: str

# --- API Endpoints ---
@app.post("/summarize")
def summarize_the_transcript(transcript: Transcript):
    summarizer = get_summarizer()
    summary = summarizer(transcript.text, max_length=150, min_length=30, do_sample=False)
    return {"summary": summary[0]['summary_text']}

@app.post("/ask")
def ask_question(qa_input: QA_Input):
    Youtubeer = get_qa()
    answer = Youtubeer(question=qa_input.question, context=qa_input.context)
    return {"answer": answer['answer']}

@app.post("/actions")
def get_action_items(transcript: Transcript):
    classifier = get_classifier()
    action_items = []
    sentences = transcript.text.split('\n')
    for sentence in sentences:
        if not sentence.strip():
            continue
        result = classifier(sentence, candidate_labels=["action item", "commitment", "task", "general discussion"])
        if result['labels'][0] != 'general discussion' and result['scores'][0] > 0.75:
            action_items.append(sentence.strip())
    return {"action_items": action_items}