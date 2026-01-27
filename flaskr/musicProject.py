from pathlib import Path
import shutil
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename

from helpers import apply_pipeline
from filters.audio import AUDIO_FILTERS
from filters.video import VIDEO_FILTERS

app = Flask(__name__, static_folder="static", template_folder="templates")

ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT / "static" / "uploads"
PROCESSED_DIR = ROOT / "static" / "processed"
TMP_DIR = ROOT / "static" / "tmp"
ALLOWED = {".mp4", ".mov", ".mkv", ".webm", ".avi"}

STATE = {
    "uploaded": False,
    "configured": False,
    "processed": False,
    "input_path": None,
    "output_path": None,
    "config": None,
}

def ok(**k): return jsonify({"ok": True, **k})
def err(msg, code=400, **k): return jsonify({"ok": False, "error": msg, **k}), code

@app.get("/")
def home():
    return render_template("project_template.html")

@app.post("/upload")
def upload():
    if STATE["uploaded"] and not STATE["processed"]:
        return err("A video is already uploaded. Delete it first.", 409)

    if "file" not in request.files:
        return err("Missing form field 'file'.", 400)
    f = request.files["file"]
    if not f.filename:
        return err("Empty filename.", 400)

    ext = Path(f.filename).suffix.lower()
    if ext not in ALLOWED:
        return err(f"Unsupported type. Allowed: {sorted(ALLOWED)}", 400)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    # clear previous
    for d in (UPLOAD_DIR, PROCESSED_DIR, TMP_DIR):
        for p in d.glob("*"):
            if p.is_file():
                p.unlink(missing_ok=True)

    name = secure_filename(f.filename)
    ip = UPLOAD_DIR / name
    f.save(ip)

    STATE.update({
        "uploaded": True,
        "configured": False,
        "processed": False,
        "input_path": str(ip),
        "output_path": None,
        "config": None,
    })
    return ok(message="Uploaded", filename=name)

@app.post("/delete")
def delete():
    if not STATE["uploaded"]:
        return err("No uploaded video to delete.", 409)
    if STATE["processed"]:
        return err("Already processed; upload already removed.", 409)

    ip = Path(STATE["input_path"]) if STATE["input_path"] else None
    if ip and ip.exists():
        ip.unlink(missing_ok=True)

    STATE.update({
        "uploaded": False,
        "configured": False,
        "processed": False,
        "input_path": None,
        "output_path": None,
        "config": None,
    })
    return ok(message="Deleted")

@app.post("/configure")
def configure():
    if not STATE["uploaded"]:
        return err("Upload a video first.", 409)
    if STATE["processed"]:
        return err("Already processed. Upload a new video.", 409)

    cfg = request.get_json(silent=True)
    if cfg is None:
        return err("Expected JSON body.", 400)
    if "audio" not in cfg or "video" not in cfg:
        return err("Config must contain 'audio' and 'video'.", 400)
    if not isinstance(cfg["audio"], list) or not isinstance(cfg["video"], list):
        return err("'audio' and 'video' must be lists.", 400)

    for item in cfg["audio"]:
        if item.get("name") not in AUDIO_FILTERS:
            return err(f"Unknown audio filter: {item.get('name')}", 400)
        if "params" in item and not isinstance(item["params"], dict):
            return err("Audio params must be an object.", 400)
        item.setdefault("params", {})

    for item in cfg["video"]:
        if item.get("name") not in VIDEO_FILTERS:
            return err(f"Unknown video filter: {item.get('name')}", 400)
        if "params" in item and not isinstance(item["params"], dict):
            return err("Video params must be an object.", 400)
        item.setdefault("params", {})

    STATE["config"] = cfg
    STATE["configured"] = True
    return ok(message="Configured", config=cfg)

@app.post("/apply")
def apply():
    if not STATE["uploaded"]:
        return err("Upload a video first.", 409)
    if not STATE["configured"]:
        return err("Configure filters first.", 409)
    if STATE["processed"]:
        return err("Already processed. Upload a new video.", 409)

    ip = Path(STATE["input_path"])
    if not ip.exists():
        return err("Uploaded file missing.", 500)

    out = PROCESSED_DIR / "output.mp4"

    try:
        apply_pipeline(ip, out, STATE["config"] or {}, TMP_DIR)
    except Exception as e:
        return err("Processing failed.", 500, details=str(e))

    # requirement: delete original after successful processing
    ip.unlink(missing_ok=True)

    STATE["processed"] = True
    STATE["output_path"] = str(out)

    return ok(message="Processed", static_url="/static/processed/output.mp4", stream_url="/stream")

@app.get("/stream")
def stream():
    if not STATE["processed"] or not STATE["output_path"]:
        return err("No processed video. Apply first.", 409)
    out = Path(STATE["output_path"])
    if not out.exists():
        return err("Processed file missing.", 500)
    return send_file(out, mimetype="video/mp4", as_attachment=False)

@app.get("/status")
def status():
    return ok(state=STATE)

if __name__ == "__main__":
    app.run(debug=True)
