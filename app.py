import os
import re
from icecream import ic
import uuid

from flask import Flask, render_template, redirect, url_for
from flask import request

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


# View All Tests
@app.route('/tests/')
def tests():
    file_list = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('tests.html', file_list=file_list)


# Create Test
@app.route('/create/', methods=['POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        path = os.path.join(app.config['UPLOAD_FOLDER'], name)
        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path, 'ans'), exist_ok=True)
        os.makedirs(os.path.join(path, 'students'), exist_ok=True)
        return redirect(url_for('detail', test_name=name))
    else:
        return render_template('error.html')


@app.route('/tests/<test_name>/', methods=['GET', 'POST'])
def detail(test_name):
    try:
        if request.method == 'POST':
            text = request.form.get("stu_ans")
            with open(f'uploads/{test_name}/ans/outputs/ans.txt', 'w+') as f:
                f.write('\n'.join(text.split('\r\n')))

        # check if uploaded answer
        have_ans = False
        file_list = os.listdir(f'uploads/{test_name}/students')
        if os.listdir(os.path.join(f'uploads/{test_name}', 'ans')):
            have_ans = True

        return render_template('detail.html', file_list=file_list, have_ans=have_ans, test_name=test_name)
    # prevent user to type a not valid url directly instead of creating a test
    except:
        return render_template('error.html')


# ############################
# ####### Answer Part ########
# ############################

# Upload Answer Image
@app.route('/tests/<test_name>/upload_ans/', methods=['GET', 'POST'])
def upload_ans(test_name):
    # Process Answer Image
    def process(test_name):
        img_path = os.path.join('uploads', test_name, 'ans')
        # feed into the model
        answer = process_img(img_path)
        return render_template('process.html', test_name=test_name, answer=answer)

    if request.method == 'GET':
        with open(f'uploads/{test_name}/ans/outputs/ans.txt', 'r') as f:
            answer = f.read()
        return render_template('process.html', test_name=test_name, answer=answer)

    if request.method == 'POST':
        extension = None
        clean_files(100)
        file = request.files.get('photo')

        if '.' in file.filename:
            extension = file.filename.rsplit('.', 1)[1]

        if file and is_extension_allowed(extension):
            file_name = 'image' + f'.{extension}'
            file.save(os.path.join('uploads', test_name, 'ans', file_name))
            return process(test_name)

    return render_template('error.html')


# View ans
@app.route('/tests/<test_name>/view_ans/', methods=['GET', 'POST'])
def view_ans(test_name):
    with open(f'uploads/{test_name}/ans/outputs/ans.txt', 'r') as f:
        answer = f.read()
    return render_template('view.html', test_name=test_name, answer=answer)


# #############################
# ####### Student Part ########
# ################$############


# #############################
# ####### Scoring Part ########
# #############################


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
