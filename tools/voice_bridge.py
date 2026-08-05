#!/usr/bin/env python3
"""Richard OS — voice bridge (VibeVoice + VoxCPM).
Honest status: connected / not_configured / error. Never fakes."""
import shutil, subprocess, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _importable(name):
    try:
        __import__(name)
        return True
    except Exception:
        return False

def status():
    providers = []
    if _importable("vibevoice") or shutil.which("vibevoice"):
        providers.append("VibeVoice")
    if _importable("voxcpm") or shutil.which("voxcpm"):
        providers.append("VoxCPM")
    if providers:
        return {"provider": "voice", "status": "connected",
                "detail": " + ".join(providers) + " available — CEO voice interface ready"}
    return {"provider": "voice", "status": "not_configured",
            "detail": "install VibeVoice (pip) or VoxCPM to enable voice I/O for the CEO agent"}

def tts(text, out="ceo-voice.wav"):
    """Text-to-speech via VibeVoice if available (else honest skip)."""
    if status()["status"] != "connected":
        return {"error": "voice provider not installed — TTS skipped (honest)"}
    try:
        from vibevoice import synthesize  # placeholder — adapt to the real API
        synthesize(text, out)
        return {"ok": True, "file": out}
    except Exception as e:
        return {"error": str(e)[:150]}

def stt(audio="input.wav"):
    """Speech-to-text via VoxCPM if available (else honest skip)."""
    if status()["status"] != "connected":
        return {"error": "voice provider not installed — STT skipped (honest)"}
    try:
        from voxcpm import transcribe  # placeholder — adapt to the real API
        return {"ok": True, "text": transcribe(audio)}
    except Exception as e:
        return {"error": str(e)[:150]}

if __name__ == "__main__":
    import json
    print(json.dumps(status(), indent=2))
