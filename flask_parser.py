import os
import random

from flask import Flask, request, render_template, redirect, jsonify, flash, url_for
from werkzeug.utils import secure_filename

from init_db import make_db_record, get_db_connection, get_post
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
    input_path = os.path.join(path, 'input')
    r = random.randint(0, 11)
    create_input_folder(input_path)
    create_random_files(r, input_path)
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
    make_db_record(dictionary)
    return jsonify(dictionary)


@app.route('/results')
def show_db():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('db_index.html', posts=posts)


@app.route('/<int:id>/edit/', methods=['GET', 'POST'])
def edit_description_by_id(id):
    post = get_post(id)

    if request.method == 'POST':
        description = request.form['description']

        conn = get_db_connection()
        conn.execute('UPDATE posts SET description = ?'
                     ' WHERE id = ?',
                     (description, id))
        conn.commit()
        conn.close()
        return redirect('/results')

    return render_template('edit.html', post=post)


@app.route('/<int:id>/get/', methods=['GET'])
def get(id):
    post = get_post(id)
    return render_template('get.html', post=post)


@app.route('/<int:id>/delete/', methods=['POST'])
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/results')


if __name__ == "__main__":
    app.run(debug=True)
