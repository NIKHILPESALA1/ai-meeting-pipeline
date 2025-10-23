#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path

# Directories
MEETINGS_DIR = "/app/data/meetings"
AUDIO_DIR = "/app/data/audio"
TRANSCRIPTS_DIR = "/app/data/transcripts"
SUMMARIES_DIR = "/app/data/summaries"

# Ensure folders exist
for d in [AUDIO_DIR, TRANSCRIPTS_DIR, SUMMARIES_DIR]:
    Path(d).mkdir(parents=True, exist_ok=True)

# Step 1: Extract audio from video (if needed) and copy audio files
for file in os.listdir(MEETINGS_DIR):
    if file.endswith((".mp4", ".wav", ".mp3")):
        src_path = os.path.join(MEETINGS_DIR, file)
        dest_path = os.path.join(AUDIO_DIR, file)
        shutil.copy(src_path, dest_path)

# Step 2: Transcribe using Whisper
for file in os.listdir(AUDIO_DIR):
    if file.endswith((".mp4", ".wav", ".mp3")):
        audio_path = os.path.join(AUDIO_DIR, file)
        print(f"Transcribing {audio_path} ...")
        subprocess.run([
            "whisper", audio_path,
            "--model", "base",
            "--language", "English",
            "--output_dir", TRANSCRIPTS_DIR,
            "--output_format", "txt"
        ])

# Step 3: Summarize and extract action items
from transformers import pipeline
import json

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

for transcript_file in os.listdir(TRANSCRIPTS_DIR):
    if transcript_file.endswith(".txt"):
        transcript_path = os.path.join(TRANSCRIPTS_DIR, transcript_file)
        with open(transcript_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Summarize
        summary = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]

        # Extract simple action items
        action_items = [line for line in text.split("\n") if "action" in line.lower() or "task" in line.lower()]

        # Save summary + action items
        output = {
            "video_name": transcript_file.replace(".txt", ""),
            "summary": summary,
            "action_items": action_items
        }

        output_file = os.path.join(SUMMARIES_DIR, transcript_file.replace(".txt", ".json"))
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4)

        print(f"Saved summary and action items to {output_file}")
