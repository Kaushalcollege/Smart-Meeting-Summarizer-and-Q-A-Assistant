from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI() #fastapi instance in app variable
# later we will be using this in the uvicorn main:app --reload

# Define the data model for the request
class Transcript(BaseModel):
    text : str

@app.get("/")
def root():
    return "backend is running"


@app.post("/summarize")
def summarize_the_transcript(transcript : Transcript):
     # For now, we just echo the text back
    # Later, the Hugging Face pipeline will go here
    return {"summary": f"You sent: {transcript.text[:50]}..."}
