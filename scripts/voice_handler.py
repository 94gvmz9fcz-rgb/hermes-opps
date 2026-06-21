#!/usr/bin/env python3
"""Voice Handler — transcribe a voice memo and extract actions.

Usage: 
  python3 voice_handler.py <path_to_audio_file>
  
Outputs structured JSON with transcript, actions, reminders, and ideas.
"""

import json, os, sys, time

WHISPER_PATH = "/opt/data/home/hermes-venv/lib/python3.13/site-packages"
sys.path.insert(0, WHISPER_PATH)

def transcribe(audio_path):
    from faster_whisper import WhisperModel
    model = WhisperModel('tiny', device='cpu', compute_type='int8')
    segments, info = model.transcribe(audio_path, beam_size=1)
    text = " ".join(seg.text for seg in segments)
    return text.strip()

def extract_actions(transcript):
    """Simple regex/rule-based extraction for common patterns."""
    import re
    
    actions = []
    reminders = []
    ideas = []
    
    lines = transcript.replace('. ', '.\n').split('\n')
    for line in lines:
        line = line.strip().lower()
        
        # Remind me to X [at time/date]
        m = re.search(r'remind me to (.+?)(?:(?:tomorrow|today|next|at|on|in)|$)', line)
        if m:
            reminders.append(m.group(1).strip())
        
        # I need to / I should / I gotta X
        m = re.search(r'(?:i need to|i should|i gotta|i have to) (.+)', line)
        if m:
            actions.append(m.group(1).strip())
        
        # What about X / Maybe X / Let's X
        m = re.search(r'(?:what about|maybe|let\'s|how about) (.+)', line)
        if m:
            ideas.append(m.group(1).strip())
    
    # If nothing matched, the whole thing is a note/idea
    if not actions and not reminders and not ideas:
        ideas.append(transcript)
    
    return actions, reminders, ideas

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: voice_handler.py <audio_path>"}))
        sys.exit(1)
    
    audio_path = sys.argv[1]
    if not os.path.exists(audio_path):
        print(json.dumps({"error": f"File not found: {audio_path}"}))
        sys.exit(1)
    
    print(f"Transcribing {audio_path}...", file=sys.stderr)
    start = time.time()
    
    transcript = transcribe(audio_path)
    actions, reminders, ideas = extract_actions(transcript)
    
    result = {
        "transcript": transcript,
        "duration_seconds": round(time.time() - start, 1),
        "actions": actions,
        "reminders": reminders,
        "ideas": ideas,
        "has_actions": len(actions) > 0 or len(reminders) > 0,
    }
    
    print(json.dumps(result, indent=2))
