from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI()

origins = [
    "http://localhost:5173", # The origin of your React frontend
    "http://localhost:3000", # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)


summarizer = pipeline("summarization", model="philschmid/distilbart-cnn-12-6-samsum")
Youtubeer = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


# Pydantic Models for Request Bodies
class Transcript(BaseModel):
    text: str

class QA_Input(BaseModel):
    question: str
    context: str

# API Endpoints


@app.post("/")
def root():
    return "Backend is Running"


@app.post("/summarize")
def summarize_the_transcript(transcript: Transcript):
    summary = summarizer(transcript.text, max_length=150, min_length=110, do_sample=False)
    return {"summary": summary[0]['summary_text']}

@app.post("/ask")
def ask_question(qa_input: QA_Input):
    answer = Youtubeer(question=qa_input.question, context=qa_input.context)
    return {"answer": answer['answer']}

@app.post("/actions")
def get_action_items(transcript: Transcript):
    action_items = []
    sentences = transcript.text.split('\n') 
    
    for sentence in sentences:
        if not sentence.strip():
            continue
            
        result = classifier(sentence, candidate_labels=["action item", "commitment", "general discussion"])
        
        if result['labels'][0] != 'general discussion' and result['scores'][0] > 0.75:
            action_items.append(sentence.strip())
            
    return {"action_items": action_items}


