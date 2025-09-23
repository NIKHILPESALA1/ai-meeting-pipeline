import os
import json
from pathlib import Path
from transformers import pipeline

# Paths
TRANSCRIPTS_DIR = "/app/data/transcripts"
SUMMARIES_DIR = "/app/data/summaries"

Path(SUMMARIES_DIR).mkdir(parents=True, exist_ok=True)

# Load summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Iterate over transcripts
for transcript_file in os.listdir(TRANSCRIPTS_DIR):
    if transcript_file.endswith(".txt"):
        transcript_path = os.path.join(TRANSCRIPTS_DIR, transcript_file)
        with open(transcript_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Summarize
        summary = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]

        # Extract simple action items (lines with keywords)
        action_items = [line for line in text.split("\n") if "action" in line.lower() or "task" in line.lower()]

        # Save summary + action items
        output = {
            "summary": summary,
            "action_items": action_items
        }

        output_file = os.path.join(SUMMARIES_DIR, transcript_file.replace(".txt", ".json"))
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4)

        print(f"Saved summary and action items to {output_file}")

