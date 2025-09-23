#!/usr/bin/env python3
import os
import json
from transformers import pipeline

# Paths
transcript_dir = "/app/data/transcripts"
summary_dir = "/app/data/summaries"

# Create summaries directory if it doesn't exist
os.makedirs(summary_dir, exist_ok=True)

# Initialize summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Summarize all transcript files
for file in os.listdir(transcript_dir):
    if file.endswith(".txt"):
        transcript_path = os.path.join(transcript_dir, file)
        with open(transcript_path, "r") as f:
            text = f.read()
        
        # Summarize
        summary_text = summarizer(text, max_length=250, min_length=50, do_sample=False)[0]['summary_text']
        
        # Create action items placeholder
        action_items = []

        # Output JSON
        output_data = {
            "summary": summary_text,
            "action_items": action_items
        }
        json_path = os.path.join(summary_dir, file.replace(".txt", ".json"))
        with open(json_path, "w") as f:
            json.dump(output_data, f, indent=4)

        # Also save a simple text summary
        text_summary_path = os.path.join(summary_dir, file.replace(".txt", "_summary.txt"))
        with open(text_summary_path, "w") as f:
            f.write(summary_text)

        print(f"Summarized {file} -> {json_path}")

