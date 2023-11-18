import os
import random

from flask import Flask, request, render_template, redirect, jsonify
from werkzeug.utils import secure_filename

from main import create_random_files, create_input_folder, read_folder

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    intput_path = os.path.join(path, 'input')
    r = random.randint(0, 100)
    create_input_folder(intput_path)
    create_random_files(r, intput_path)
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return 'No file part'

        files = request.files.getlist("files[]")
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                return f"Unsupported {file.filename}"
        return redirect('/summary')

    return 'Files does not upload'


@app.route('/summary')
def summary():
    dictionary = read_folder(app.config['UPLOAD_FOLDER'])
    return jsonify(dictionary)


if __name__ == "__main__":
    app.run(debug=True)
