#!/usr/bin/env python3
"""Richard OS — Home hierarchy: room-wise agents that control devices."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from agent_lib import call_llm, log_run, read_memory
import home_bridge
from orchestrator import load_domains, find_agent

ROOMS = {
    "light":  ("living-room", "lights"),
    "tv":     ("living-room", "tv"),
    "ac":     ("living-room", "ac"),
    "temperature": ("living-room", "ac"),
    "kitchen": ("kitchen", "appliances"),
    "bedroom": ("bedroom", "lights"),
    "alarm":  ("bedroom", "alarm"),
    "camera": ("security", "cameras"),
    "lock":   ("security", "door-lock"),
}

ACTIONS = {
    "on": "on", "turn on": "on", "off": "off", "turn off": "off",
    "lock": "lock", "unlock": "unlock", "arm": "arm", "disarm": "disarm",
}

def main():
    text = " ".join(sys.argv[1:])
    if not text:
        print("Usage: python scripts/home_agents.py <command>")
        print("  e.g. 'turn on the living room lights'")
        print("  e.g. 'set AC to 22 degrees'")
        print("  e.g. 'lock the door' / 'arm the cameras'")
        print("  e.g. 'what's the state of the bedroom?'")
        print("\nDevices:", json_dumps(home_bridge.list_devices()))
        return

    low = text.lower()
    # find room + device
    room, device = None, None
    for kw, (r, d) in ROOMS.items():
        if kw in low:
            room, device = r, d
            break
    if not room:
        print(f"❓ No device matched for: {text!r}")
        print("   Try: lights, tv, ac, kitchen, bedroom, alarm, camera, lock")
        return

    # find action
    action = None
    for kw, a in ACTIONS.items():
        if kw in low:
            action = a
            break
    if "state" in low or "status" in low:
        print(home_bridge.get_state(room))
        return

    if not action:
        # let the LLM interpret the command
        mem = read_memory()[:1000]
        prompt = (f"You are the {room} room agent. Autonomy 2 (recommend only). "
                  f"Command: {text}\nCurrent state: {home_bridge.get_state(room)}\n"
                  f"Decide the device action and reply with JSON: {{\"action\": \"...\", \"params\": {{}}}}")
        out = call_llm(prompt, "deepseek-v4-flash-free")
        print(out[:500])
        log_run(f"home/{room}", "llm-interpreted", out[:120])
        return

    result = home_bridge.device_action(room, device, action)
    print(f"🏠 {room}/{device} → {action}: {result}")
    log_run(f"home/{room}", f"{device} {action}", str(result))

def json_dumps(obj):
    import json
    return json.dumps(obj, indent=2)

if __name__ == "__main__":
    main()
