#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
import shutil
import json
from transformers import pipeline

# -----------------------------
# Directories
# -----------------------------
MEETINGS_DIR = "/app/data/meetings"
AUDIO_DIR = "/app/data/audio"
TRANSCRIPTS_DIR = "/app/data/transcripts"
SUMMARIES_DIR = "/app/data/summaries"

# Ensure folders exist
for d in [AUDIO_DIR, TRANSCRIPTS_DIR, SUMMARIES_DIR]:
    Path(d).mkdir(parents=True, exist_ok=True)

# -----------------------------
# Step 1: Extract audio from videos
# -----------------------------
for file in os.listdir(MEETINGS_DIR):
    if file.endswith(".mp4"):
        video_path = os.path.join(MEETINGS_DIR, file)
        audio_file = os.path.splitext(file)[0] + ".wav"
        audio_path = os.path.join(AUDIO_DIR, audio_file)

        if os.path.exists(audio_path):
            print(f"[SKIP] Audio already exists for {file}")
            continue

        print(f"[INFO] Extracting audio from {file} ...")
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", audio_path
            ], check=True)
            print(f"[SUCCESS] Audio saved to {audio_path}")
        except subprocess.CalledProcessError:
            print(f"[ERROR] Failed to extract audio from {file}")
            continue

# -----------------------------
# Step 2: Transcribe audio using Whisper
# -----------------------------
for audio_file in os.listdir(AUDIO_DIR):
    if not audio_file.endswith(".wav"):
        continue

    audio_path = os.path.join(AUDIO_DIR, audio_file)
    transcript_file = os.path.splitext(audio_file)[0] + ".txt"
    transcript_path = os.path.join(TRANSCRIPTS_DIR, transcript_file)

    if os.path.exists(transcript_path):
        print(f"[SKIP] Transcript already exists for {audio_file}")
        continue

    print(f"[INFO] Transcribing {audio_file} ...")
    try:
        subprocess.run([
            "whisper", audio_path,
            "--model", "base",
            "--language", "English",
            "--output_dir", TRANSCRIPTS_DIR,
            "--output_format", "txt"
        ], check=True)
        print(f"[SUCCESS] Transcript saved to {transcript_path}")
    except subprocess.CalledProcessError:
        print(f"[ERROR] Failed to transcribe {audio_file}")
        continue

# -----------------------------
# Step 3: Summarize transcripts and extract action items
# -----------------------------
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

for transcript_file in os.listdir(TRANSCRIPTS_DIR):
    if not transcript_file.endswith(".txt"):
        continue

    transcript_path = os.path.join(TRANSCRIPTS_DIR, transcript_file)
    summary_path = os.path.join(SUMMARIES_DIR, transcript_file.replace(".txt", ".json"))

    if os.path.exists(summary_path):
        print(f"[SKIP] Summary already exists for {transcript_file}")
        continue

    with open(transcript_path, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"[INFO] Summarizing {transcript_file} ...")
    try:
        summary_text = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
    except Exception as e:
        print(f"[ERROR] Summarization failed for {transcript_file}: {e}")
        summary_text = ""

    # Extract simple action items
    action_items = [line.strip() for line in text.split("\n") if "action" in line.lower() or "task" in line.lower()]

    # Save summary + action items
    output = {
        "video_name": transcript_file.replace(".txt", ""),
        "summary": summary_text,
        "action_items": action_items
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    print(f"[SUCCESS] Summary + action items saved to {summary_path}")
