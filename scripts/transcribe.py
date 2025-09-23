#!/usr/bin/env python3
import subprocess
import os

# Paths
audio_dir = "/app/data/audio"
transcript_dir = "/app/data/transcripts"

# Make sure transcript directory exists
os.makedirs(transcript_dir, exist_ok=True)

# Transcribe all audio files in the directory
for file in os.listdir(audio_dir):
    if file.endswith(".wav") or file.endswith(".mp3") or file.endswith(".mp4"):
        audio_path = os.path.join(audio_dir, file)
        print(f"Transcribing {audio_path} ...")
        subprocess.run([
            "whisper", audio_path,
            "--model", "base",
            "--language", "English",
            "--output_dir", transcript_dir,
            "--output_format", "txt"
        ])
print("All audio files transcribed.")


