from flask import Flask, request, render_template, redirect, url_for, jsonify
import os, uuid, json
from utils.resume_parser import extract_text_from_file
from utils.nlp_matcher import match_candidates_for_job

DB_PATH = "database.json"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def load_db():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({"candidates": [], "jobs": []}, f)
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    db = load_db()
    return render_template("index.html", candidates=db["candidates"], jobs=db["jobs"])

@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    name = request.form.get("name", "Unknown")
    file = request.files.get("resume")
    if not file:
        return redirect(url_for("index"))
    filename = str(uuid.uuid4()) + "_" + file.filename
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    text = extract_text_from_file(path)
    candidate = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "filename": filename,
        "text": text
    }
    db = load_db()
    db["candidates"].append(candidate)
    save_db(db)
    return redirect(url_for("index"))

@app.route("/add_job", methods=["POST"])
def add_job():
    title = request.form.get("title", "Untitled Job")
    desc = request.form.get("description", "")
    job = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "description": desc
    }
    db = load_db()
    db["jobs"].append(job)
    save_db(db)
    return redirect(url_for("index"))

@app.route("/match/<job_id>")
def match(job_id):
    db = load_db()
    job = next((j for j in db["jobs"] if j["id"]==job_id), None)
    if not job:
        return "Job not found", 404
    matches = match_candidates_for_job(job["description"], db["candidates"])
    # attach scores
    for m in matches:
        m["fit_score"] = round(m["score"], 3)
    return render_template("matches.html", job=job, matches=matches)

# API endpoints for quick evaluation
@app.route("/api/jobs", methods=["GET"])
def api_jobs():
    return jsonify(load_db()["jobs"])

@app.route("/api/candidates", methods=["GET"])
def api_candidates():
    return jsonify(load_db()["candidates"])

@app.route("/api/match/<job_id>", methods=["GET"])
def api_match_job(job_id):
    db = load_db()
    job = next((j for j in db["jobs"] if j["id"]==job_id), None)
    if not job:
        return jsonify({"error":"not found"}), 404
    matches = match_candidates_for_job(job["description"], db["candidates"])
    return jsonify({"job_id": job_id, "matches": matches})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
