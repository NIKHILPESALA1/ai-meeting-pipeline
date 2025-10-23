#!/usr/bin/env python3
import os
import json
from pathlib import Path
import subprocess
from transformers import pipeline

# Paths
MEETINGS_DIR = "/app/data/meetings"
AUDIO_DIR = "/app/data/audio"
TRANSCRIPTS_DIR = "/app/data/transcripts"
SUMMARIES_DIR = "/app/data/summaries"
PROCESSED_FILE = "/app/data/processed_videos.json"

# Create directories if missing
for d in [AUDIO_DIR, TRANSCRIPTS_DIR, SUMMARIES_DIR]:
    Path(d).mkdir(parents=True, exist_ok=True)

# Load processed videos
if Path(PROCESSED_FILE).exists():
    with open(PROCESSED_FILE, "r") as f:
        processed = set(json.load(f))
else:
    processed = set()

# Identify new videos
new_videos = [f for f in os.listdir(MEETINGS_DIR) if f.endswith(".mp4") and f not in processed]

# Load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

for video in new_videos:
    video_path = os.path.join(MEETINGS_DIR, video)
    print(f"🔹 Processing new video: {video}")

    # 1️⃣ Extract audio
    audio_output = os.path.join(AUDIO_DIR, f"{Path(video).stem}.wav")
    subprocess.run(["ffmpeg", "-y", "-i", video_path, audio_output])

    # 2️⃣ Transcribe
    subprocess.run([
        "whisper", audio_output,
        "--model", "base",
        "--language", "English",
        "--output_dir", TRANSCRIPTS_DIR,
        "--output_format", "txt"
    ])

    # 3️⃣ Summarize and extract action items
    transcript_file = os.path.join(TRANSCRIPTS_DIR, f"{Path(video).stem}.txt")
    with open(transcript_file, "r", encoding="utf-8") as f:
        text = f.read()

    summary_text = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
    action_items = [line for line in text.split("\n") if "action" in line.lower() or "task" in line.lower()]

    summary_file = os.path.join(SUMMARIES_DIR, f"{Path(video).stem}.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({"summary": summary_text, "action_items": action_items}, f, indent=4)

    print(f"✅ Finished processing {video}")

    # Mark video as processed
    processed.add(video)

# Save processed videos
with open(PROCESSED_FILE, "w") as f:
    json.dump(list(processed), f)
