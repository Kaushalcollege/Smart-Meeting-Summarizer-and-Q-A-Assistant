from transformers import pipeline

# 1. Initialize the pipeline
summarizer = pipeline("summarization", model="philschmid/distilbart-cnn-12-6-samsum")

# 2. Use the pipeline
meeting_text = """
"""

summary = summarizer(meeting_text, max_length=100, min_length=95, do_sample=False)
print(summary)