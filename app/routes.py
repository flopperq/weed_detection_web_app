from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import subprocess
import uuid
import shutil

app = Flask(__name__)


DETECTION_FILES = 'uploads'
RUN_NAME = 'expert'
IMAGE_SIZE = 640
CONF_THRESH = 0.13
WEIGHTS_PATH = 'C:/Users/Ivan/PycharmProjects/pythonProject1/yolov5/runs/train/exp/weights/best.pt'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)
        upload_dir = os.path.join(basepath, DETECTION_FILES)
        os.makedirs(upload_dir, exist_ok=True)

        unique_filename = str(uuid.uuid4()) + "_" + f.filename
        upload_path = os.path.join(upload_dir, unique_filename)
        f.save(upload_path)

        # Вызов команды для запуска detect.py
        command = [
            'python', 'C:/Users/Ivan/PycharmProjects/pythonProject1/yolov5/detect.py',
            '--source', upload_path,
            '--weights', WEIGHTS_PATH,
            '--name', RUN_NAME,
            '--img', str(IMAGE_SIZE),
            '--conf-thres', str(CONF_THRESH),
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        if result.returncode != 0:
            return f"Error: {result.stderr.decode('utf-8')}"

        # Поиск выходных файлов
        output_dir = os.path.join(basepath, 'yolov5', 'runs', 'detect', RUN_NAME)
        output_files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]

        matching_files = [f for f in output_files if unique_filename in f]

        if matching_files:
            # Вывод только файлов, которые совпадают по имени

            return render_template('index.html', files=matching_files, run_name=RUN_NAME)
        else:
            return "No matching files found."

    return render_template('index.html')

@app.route('/uploads/expert/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(DETECTION_FILES, RUN_NAME), filename)
