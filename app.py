import os
import re
from icecream import ic
import uuid

from flask import Flask, render_template, redirect, url_for
from flask import request, send_from_directory

from upload import *
from process import process_img
from result import *

app = Flask(__name__)

# config
# save location
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
# file size constraint
app.config['MAX_CfONTENT_LENGTH'] = 1024 * 1024 * 8  # not used (future work)


# Main Page
@app.route('/')
def index():
    return render_template("index.html")


# Create Test
@app.route('/create/', methods=['POST'])
def create():
    print('creating')
    filename = ''
    if request.method == 'POST':
        name = request.form.get('name')
        print(name)
        path = os.path.join(app.config['UPLOAD_FOLDER'], name)
        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path, 'ans'), exist_ok=True)
        return redirect(url_for('detail', test_name=name))
    else:
        return render_template('error.html')


@app.route('/test/<test_name>/')
def detail(test_name):
    # check if uploaded answer
    have_ans = False
    file_list = os.listdir(f'uploads/{test_name}').remove('ans')
    print(file_list)
    if os.listdir(os.path.join(f'uploads/{test_name}', 'ans')):
        have_ans = True
    print(have_ans)
    return render_template('detail.html', file_list=file_list, have_ans=have_ans, test_name=test_name)


# Upload Image
@app.route('/test/<test_name>/upload_ans/', methods=['POST'])
def upload_ans(test_name):
    print('uploading test ans')
    print(test_name)
    extension = None
    if request.method == 'POST':
        clean_files(100)
        file = request.files.get('photo')

        if '.' in file.filename:
            extension = file.filename.rsplit('.', 1)[1]

        if file and is_extension_allowed(extension):
            file_name = 'image' + f'.{extension}'
            file.save(os.path.join('uploads', test_name, 'ans', file_name))
            process(test_name)

    return render_template('error.html')



# Process Image
def process(test_name):
    img_path = os.path.join('uploads', test_name, 'ans')
    # feed into the model
    stu_ans = process_img(img_path)
    return render_template('process.html', stu_ans=stu_ans)


# # View ans
# @app.route('/test/<test_name>/view_ans')
# def view_ans(test_name):



# # Get Image
# @app.route('/uploaded/<filename>')
# def uploaded(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# View Test
# @app.route('/view/')
# def view():
#     pass
#
#
# # Upload Image
# @app.route('/upload/', methods=['POST'])
# def upload():
#     print('uploading')
#     img_url = None
#     extension = None
#     if request.method == 'POST':
#         clean_files(100)
#         file = request.files.get('photo')
#
#         if '.' in file.filename:
#             extension = file.filename.rsplit('.', 1)[1]
#
#         if file and is_extension_allowed(extension):
#             file_name = str(uuid.uuid1()) + f'.{extension}'
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
#             redirect(url_for('uploaded', filename=file_name))
#
#     return render_template('error.html')
#
#
#
# # Process Image
# @app.route('/process/<filename>')
# def process(img_url):
#     img_path = os.path.join('uploads', img_url.split('/')[-1])
#     # feed into the model
#     stu_ans = process_img(img_path)
#     return render_template('process.html', img_url=img_url, stu_ans=stu_ans)
#
#
# # Show Result
# @app.route('/result/', methods=['POST'])
# def result():
#     detail = []
#     correct = 0
#     total = 0
#     text = ''
#     answer = """商王东迁成都
# 晋楚双方城濮大战后晋文公成为中原霸主
# 赤壁之战
# 郡县制度
# 罢黜百家，独尊儒术
# """
#     if request.method == 'POST':
#         text = request.form.get("stu_ans")
#         detail, correct, total = calculate(text, answer)
#     return render_template('result.html', detail=detail, correct=correct, total=total)


if __name__ == '__main__':
    app.run(debug=True)
    app.jinja_env.auto_reload = True
