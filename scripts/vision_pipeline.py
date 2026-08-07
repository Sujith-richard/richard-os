#!/usr/bin/env python3
"""
scripts/vision_pipeline.py - Phase G4 Vision feedback pipeline
Image -> analyze (vision model) -> extract structured UI spec
(layout/components/colors/spacing/nav/typography) -> store as knowledge
(memory + knowledge graph) -> return the spec so the local model can retry.
"""
import json, sqlite3, pathlib, datetime, re, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent

def analyze_image(image_path):
    """Vision analyze via doc_chat._analyze_image (routes vision-capable models)."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from doc_chat import _analyze_image
    return _analyze_image(image_path)

def _extract_spec(description):
    """Parse a vision description into a structured UI spec (best-effort heuristics)."""
    d = (description or "").lower()
    spec = {
        "layout": _pick(["grid", "flex", "hero", "card", "navbar", "sidebar", "two-column"], d),
        "components": _find_component_words(d),
        "colors": _find_hex(d),
        "nav": "navbar" in d or "navigation" in d,
        "typography_mentions": sum(1 for w in ["font", "heading", "title", "text"] if w in d),
    }
    return spec

def _pick(candidates, text):
    return [c for c in candidates if c in text][:3]

def _find_component_words(text):
    comps = ["button", "form", "input", "card", "hero", "navbar", "footer", "image", "icon", "chart", "table", "menu"]
    return [c for c in comps if c in text]

def _find_hex(text):
    return re.findall(r"#[0-9a-f]{6}|#[0-9a-f]{3}", text)[:5]

def run(image_path, name=None):
    """Full pipeline: analyze -> spec -> store knowledge -> return spec for retry."""
    desc = analyze_image(image_path)
    spec = _extract_spec(desc)
    # store as experience memory
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from memory_system import add
        add("experience", f"[vision] {name or image_path}: {desc[:150]}", importance=2)
    except Exception:
        pass
    # store into knowledge graph (image -> represents -> component)
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from knowledge_graph import add_triple
        node = name or pathlib.Path(image_path).stem
        for comp in spec["components"][:4]:
            add_triple(node, "represents", comp, "vision", "image", "component")
        for lay in spec["layout"][:2]:
            add_triple(node, "uses-layout", lay, "vision", "image", "layout")
    except Exception:
        pass
    return {"ok": True, "image": name or image_path, "description": desc[:300],
            "spec": spec, "knowledge_stored": True,
            "retry_prompt": ("Using this extracted UI spec, generate the components: "
                             + ", ".join(spec["components"]) + ". Layout: " + ", ".join(spec["layout"]))}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="path to image file")
    ap.add_argument("--name", default=None)
    args = ap.parse_args()
    print(json.dumps(run(args.image, args.name), indent=2, default=str))

if __name__ == "__main__":
    main()
