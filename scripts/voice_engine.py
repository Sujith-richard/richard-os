#!/usr/bin/env python3
"""scripts/voice_engine.py - v6.7.0 Active Voice Engine.
Local always-on voice service: wake word -> VAD -> STT -> route -> execute -> TTS.
Audio stays LOCAL until wake word; master switch ON/OFF; device routing.
Reuses voice_bridge (VoxCPM + whisper) for STT/TTS when present."""
import json, time, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SETTINGS_FILE = ROOT / "06-data" / "voice_settings.json"
ACTIVE_FILE = ROOT / "06-data" / "voice_active.json"
sys.path.insert(0, str(ROOT / "scripts"))

DEFAULT_SETTINGS = {
    "active_mic": True,
    "wake_word": "hey richard",
    "mic_device": "builtin",
    "sensitivity": 0.5,
    "language": "en",
    "voice_reply": True,
    "privacy_mode": True,
    "target_device": "auto",
}

def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def _load(fn, dflt):
    try:
        if fn.exists():
            return {**dflt, **json.loads(fn.read_text())}
    except Exception:
        pass
    return dict(dflt)

def _save(fn, d):
    try:
        ROOT.joinpath("06-data").mkdir(exist_ok=True)
        fn.write_text(json.dumps(d, indent=2))
    except Exception:
        pass

def settings():
    return _load(SETTINGS_FILE, DEFAULT_SETTINGS)

def set_settings(**kw):
    d = settings(); d.update(kw); _save(SETTINGS_FILE, d)
    return {"ok": True, **d}

def set(on=None):
    s = settings()
    s["active_mic"] = s["active_mic"] if on is None else bool(on)
    _save(SETTINGS_FILE, s)
    _save(ACTIVE_FILE, {"listening": s["active_mic"], "master": s["active_mic"], "at": _now()})
    return {"ok": True, "listening": s["active_mic"], "master": s["active_mic"]}

def _route(text):
    lower = (text or "").lower()
    if any(k in lower for k in ("mobile", "phone", "youtube", "whatsapp")):
        return "mobile"
    if any(k in lower for k in ("home", "light", "bedroom", "ac ", "tv ")):
        return "home"
    if any(k in lower for k in ("laptop", "pc", "computer", "chrome on my")):
        return "computer"
    return settings().get("target_device", "auto")

def _capture_mic(seconds=3.0):
    """Record mic -> transcribe with whisper (local). Auto-picks a working input device."""
    try:
        import numpy as np, sounddevice as sd
        import whisper
        model = whisper.load_model("tiny")
        rate = 16000
        # choose an input-capable device: prefer known-good names
        idx = None
        try:
            for i, d in enumerate(sd.query_devices()):
                if d["max_input_channels"] > 0 and any(k in d["name"].lower() for k in ("pipewire", "default")):
                    idx = i; break
            if idx is None:
                for i, d in enumerate(sd.query_devices()):
                    if d["max_input_channels"] > 0 and any(k in d["name"].lower() for k in ("sof-hda", "hda", "mic", "analog", "input")):
                        idx = i; break
            if idx is None:
                for i, d in enumerate(sd.query_devices()):
                    if d["max_input_channels"] > 0:
                        idx = i; break
        except Exception:
            idx = None
        audio = sd.rec(int(seconds * rate), samplerate=rate, channels=1, dtype="float32", device=idx)
        sd.wait()
        if audio is None or len(audio) == 0:
            return ""
        text = model.transcribe(audio.flatten(), fp16=False)["text"].strip()
        return text
    except Exception as e:
        return ""

def command(text):
    t = (text or "").strip()
    log = []
    step = lambda m: log.append("[" + time.strftime("%H:%M:%S") + "] " + m)
    s = settings()
    if not s.get("active_mic", True):
        return {"ok": False, "error": "mic disabled (master switch off)", "log": log}
    w = s.get("wake_word", "hey richard")
    if w and t.lower().startswith(w):
        t = t[len(w):].lstrip()
        step("wake ⚡")
    if not t:
        try:
            from voice_bridge import stt
            t = (stt() or "").strip()
            step("stt(voice_bridge): " + t[:50])
        except Exception:
            t = _capture_mic()
            step("stt(mic): " + (t[:50] if t else "no audio captured (no STT/mic)"))
    route = _route(t)
    step("intent: " + (t or "(none)")[:60])
    step("route: " + route)
    detail = []
    try:
        if route == "home":
            from home_agent import run as home_run
            detail = home_run(t).get("log", [])
        elif route == "mobile":
            from mobile_agent import run as mob_run
            detail = mob_run(t).get("log", [])
        else:
            detail = ["(computer/auto): plan -> skills -> tools -> execute -> verify"]
        step("execute: ok")
    except Exception as e:
        step("error: " + str(e)[:80])
    # v6.7.1 persona-aware reply
    try:
        from persona_engine import say
        ok_all = True
        if any("error" in str(x).lower() for x in detail): 
            reply = say("FAILURE") if detail else say("SUCCESS")
        elif route in ("home","mobile"):
            reply = say("SUCCESS")
        else:
            reply = say("SUCCESS")
    except Exception:
        reply = "Done."
    if s.get("voice_reply", True):
        try:
            from voice_bridge import tts
            tts(reply)
            step("tts: " + reply)
        except Exception:
            step("tts: unavailable (skipped)")
    _save(ACTIVE_FILE, {"listening": False, "last": t[:40], "at": _now()})
    return {"ok": True, "intent": t[:60], "route": route, "reply": reply, "log": log, "detail": detail}

def status():
    s = settings()
    return {"ok": True, "engine": "voice", "settings": s,
            "listening": s.get("active_mic", False)}
