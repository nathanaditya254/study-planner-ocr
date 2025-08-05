import os
import json
from flask import Flask, redirect, render_template, request, jsonify, url_for
from flask_cors import CORS
from datetime import datetime, timedelta
from ocr_handler import extract_and_parse

app = Flask(__name__)
CORS(app)
tasks = []
breaks = []
task_id_counter = 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-task', methods=['POST'])
def add_task():
    global task_id_counter
    data = request.get_json()
    req_fields = ['name', 'due_date', 'duration', 'type']

    if not all(field in data for field in req_fields):
        return jsonify({"error": "Missing fields"}), 400

    try:
        due_date = datetime.fromisoformat(data["due_date"])
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    new_task = {
        'id': task_id_counter,
        'name': data['name'],
        'due_date': due_date,
        'duration': int(data['duration']),
        "type": data["type"],
        'start_time': None,
        'status': 'pending',
        'order': task_id_counter
    }
    tasks.append(new_task)
    task_id_counter += 1
    return jsonify({"message": "Task added", "id": new_task['id']})

@app.route('/schedule')
def gen_sched():
    sched = []
    if not tasks:
        return jsonify([])

    sorted_tasks = sorted(tasks, key=lambda t: t['due_date'])
    current_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    for task in sorted_tasks:
        task_start = current_time
        task_end = task_start + timedelta(minutes=task["duration"])

        sched.append({
            "start": task_start.strftime("%I:%M %p"),
            "end": task_end.strftime("%I:%M %p"),
            "task": task["name"]
        })
        current_time = task_end

        # break time logic
        if task["duration"] >= 45:
            current_time += timedelta(minutes=10)
        elif task["duration"] >= 30:
            current_time += timedelta(minutes=5)

    return jsonify(sched)

@app.route('/start-break', methods=['POST'])
def start_break():
    data = request.get_json()
    if 'duration' not in data:
        return jsonify({'error': 'Duration missing'}), 400
    try:
        duration = int(data['duration'])
    except ValueError:
        return jsonify({"error": "Duration must be an integer"}), 400

    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration)

    breaks.append({
        "start_time": start_time,
        "duration": duration,
        "end_time": end_time
    })

    return jsonify({
        "message": "Break started",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    })

@app.route('/breaks')
def get_breaks():
    total_breaks = len(breaks)

    total_time = sum(b['duration'] for b in breaks)

    break_list = []
    for b in breaks:
        break_list.append({
            "start_time": b['start_time'].strftime("%Y-%m-%d %H:%M"),
            "duration": b['duration'],
            "end_time": b['end_time'].strftime("%Y-%m-%d %H:%M")
        })

    return jsonify({
        "total_breaks": total_breaks,
        "total_break_time": total_time,
        "breaks": break_list
    })

@app.route("/upload", methods=["POST"])
def handle_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    image = request.files["file"]
    if image.filename == "":
        return jsonify({"error": "No selected file"}), 400

    image_path = "temp.png"
    image.save(image_path)

    result = extract_and_parse(image_path)
    os.remove(image_path)

    if "error" in result:
        return jsonify(result), 400

    try:
        structured_task = json.loads(result)
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse task from AI response."}), 400

    return jsonify(structured_task)

if __name__ == "__main__":
    app.run(debug=True)
