from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__)

# Load syllabus once at startup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "courses.json")

try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        COURSES = json.load(f)
except FileNotFoundError:
    COURSES = {}
    print("Warning: courses.json not found!")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculator/<branch>")
def calculator(branch):
    branch = branch.upper()
    if branch not in COURSES:
        return f"Branch '{branch}' not found.", 404
    
    course_data = COURSES[branch]
    # Flatten or prepare data for easier Jinja looping if needed
    return render_template(
        "calculator.html",
        branch=branch,
        course_name=course_data.get("courseName", branch),
        years=course_data.get("courseUnits", [])  # pass years array
    )
if __name__ == "__main__":
    app.run(debug=True, port=5001)  # port 5001 to avoid conflict