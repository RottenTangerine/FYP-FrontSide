import os
import re
import uuid

from flask import Flask, render_template, redirect, url_for
from flask import request, send_from_directory

from upload import *
from process import *
from result import *

app = Flask(__name__)

# config
# save location
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'Uploads')
# file size constraint
app.config['MAX_CfONTENT_LENGTH'] = 1024 * 1024 * 8  # not used (future work)


# Main Page
@app.route('/')
def index():
    return render_template("index.html")


# Upload Image
@app.route('/upload/', methods=['POST'])
def upload():
    img_url = None
    extension = None
    if request.method == 'POST':
        clean_files(100)
        file = request.files.get('photo')

        if '.' in file.filename:
            extension = file.filename.rsplit('.', 1)[1]

        if file and is_extension_allowed(extension):
            file_name = str(uuid.uuid1()) + f'.{extension}'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            img_url = url_for('uploaded', filename=file_name)
    return process(img_url)


# Get Image
@app.route('/uploaded/<filename>')
def uploaded(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Process Image
@app.route('/process/<filename>')
def process(img_url):
    # feed into the model
    stu_ans = """b
c
a
b
d
468000
岳阳楼
Machine Learning
20m"""
    return render_template('process.html', img_url=img_url, stu_ans=stu_ans)


# Show Result
@app.route('/result/', methods=['POST'])
def result():
    detail = []
    correct = 0
    total = 0
    text = ''
    answer = """a
c
b
b
d
468000
万里长城
Machine Learning
20cm"""
    if request.method == 'POST':
        text = request.form.get("stu_ans")
        detail, correct, total = calculate(text, answer)
    return render_template('result.html', detail=detail, correct=correct, total=total)


if __name__ == '__main__':
    app.run(debug=True)
    app.jinja_env.auto_reload = True
