#!/usr/bin/env python3
"""scripts/persona_engine.py - v6.7.1 Persona Engine for Richard Voice.
Maps response INTENT TYPES to persona-filtered phrases (JARVIS/Professional/Friendly/Minimal/Custom).
Brain decides WHAT; Persona decides HOW to say it. Configurable address + detail level."""
import json, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONF = ROOT / "06-data" / "persona_settings.json"

PERSONAS = {
  "jarvis": {
    "WAKE": ["Welcome, {addr}. What can I do for you?", "At your service."],
    "ACK":  ["Certainly, {addr}.", "Right away, {addr}."],
    "START":["The process has started, {addr}.", "Working on it."],
    "PROGRESS": ["The process is progressing well, {addr}.", "Under way."],
    "WAIT": ["I'm on the flow now, {addr}.", "Bear with me."],
    "SUCCESS": ["The process completed successfully, {addr}.", "Complete."],
    "PARTIAL": ["Mostly done, {addr}. One step needs your consent.", "Partial success."],
    "FAILURE": ["I couldn't complete that operation, {addr}.", "Failed."],
    "CONFIRM": ["This requires your confirmation, {addr}.", "Approve?"],
    "GOODBYE": ["Very well, {addr}.", "Goodbye."],
  },
  "professional": {
    "WAKE":   ["Good day, {name}. How can I assist?"],
    "ACK":    ["Understood, {addr}."],
    "START":  ["The operation has commenced."],
    "PROGRESS": ["The task is in progress."],
    "WAIT":   ["Processing — please hold."],
    "SUCCESS":["The operation completed successfully."],
    "PARTIAL":["The operation mostly completed; one item needs attention."],
    "FAILURE":["The operation could not be completed."],
    "CONFIRM":["This action needs your approval."],
    "GOODBYE":["Goodbye."],
  },
  "friendly": {
    "WAKE":   ["Hey {addr}! What can I do for you?"],
    "ACK":    ["Sure thing!", "Got it!"],
    "START":  ["On it!", "Starting now."],
    "PROGRESS": ["Almost just a sec."],
    "WAIT":   ["Working hard."],
    "SUCCESS":["Done!", "All good!"],
    "PARTIAL":["Mostly done — small thing left for you."],
    "FAILURE":["Oops, that didn't work."],
    "CONFIRM":["Quick check — can you approve?"],
    "GOODBYE":["Ciao!", "Talk soon!"],
  },
  "minimal": {
    "WAKE": ["Ready."], "ACK": ["OK."], "START": ["Go."], "PROGRESS": ["…"],
    "WAIT": ["…"], "SUCCESS": ["Done."], "PARTIAL": ["Partial."], "FAILURE": ["Failed."],
    "CONFIRM": ["Approve?"], "GOODBYE": ["Bye."],
  },
}

DEFAULT = {
  "persona": "jarvis",
  "address": "sir",
  "greeting": "",
  "response_detail": "normal",
  "voice": "",
  "speed": 1.0,
}

def _load():
    try:
        if CONF.exists():
            return {**DEFAULT, **json.loads(CONF.read_text())}
    except Exception:
        pass
    return dict(DEFAULT)

def _save(d):
    try:
        CONF.parent.mkdir(exist_ok=True); CONF.write_text(json.dumps(d, indent=2))
    except Exception:
        pass

def settings(): return _load()
def set_persona(**kw):
    d = _load(); d.update(kw); _save(d); return {"ok": True, **d}

def god_name():
    return _load().get("address", "sir")

def say(intent):
    """Pick a phrase for an intent type under the active persona."""
    s = _load(); kind = s.get("persona", "jarvis")
    pset = PERSONAS.get(kind, PERSONAS["jarvis"])
    phrase = pset.get(intent)
    if isinstance(phrase, list): phrase = random.choice(phrase) if phrase else None
    if phrase is None: phrase = "Done."
    return phrase.format(name=god_name(), addr=god_name())

def response(intent):
    return {"ok": True, "persona": _load().get("persona"), "intent": intent, "phrase": say(intent)}
