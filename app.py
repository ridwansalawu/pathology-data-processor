from flask import Flask, render_template, request, jsonify
from mains import produce
import tempfile
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    begins = request.form["begins"]
    ends = request.form["ends"]
    file = request.files["file"]

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    temp_dir = tempfile.gettempdir()
    input_path = os.path.join(temp_dir, file.filename)
    file.save(input_path)

    # Output path is temporary — GUI will move it
    output_path = os.path.join(temp_dir, f"processed_{file.filename}")

    produce(begins, ends, input_path, output_path)

    return jsonify({"output_path": output_path})
