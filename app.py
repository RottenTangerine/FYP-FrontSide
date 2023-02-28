import json
import os

import pandas as pd
from icecream import ic

from flask import Flask, render_template, redirect, url_for
from flask import request
import base64

from upload import *
from process import process_img
from result import *

from PIL import Image
import sqlite3

app = Flask(__name__)

# config
# save location
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'temporary')
# file size constraint
app.config['MAX_CfONTENT_LENGTH'] = 1024 * 1024 * 8  # not used (future work)


# Main Page
@app.route('/')
def index():
    # database
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT t.id, t.test_name, COUNT(p.id) AS paper_number,
    CASE WHEN t.ans_txt IS NULL THEN 0 ELSE 1 END AS have_ans
    FROM alltest t
    LEFT JOIN allpaper p ON t.id = p.test_id
    GROUP BY t.id, t.test_name;""")
    tests_meta = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", tests_meta=tests_meta)


@app.route('/tests/')
def tests():
    return redirect(url_for('index'))


# Create Test
@app.route('/create/', methods=['POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('name')

        # connect database
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alltest (test_name, author) VALUES (?, ?);", [name, 'default'])
        cursor.execute(f"SELECT id FROM alltest ORDER BY id DESC LIMIT 1;")
        id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('detail', test_id=id))
    else:
        return render_template('error.html', error_msg='Create error')


@app.route('/tests/<test_id>/', methods=['GET', 'POST'])
def detail(test_id):
    # try:
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ans_txt FROM alltest WHERE id = ?;", [test_id])
    answer = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    # get all paper of the test
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM allpaper WHERE test_id = ?;", [test_id])
    papers_meta = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('Test/detail.html', papers_mata=papers_meta, have_ans=bool(answer), test_id=test_id)


# ############################
# ####### Answer Part ########
# ############################

@app.route('/tests/<test_id>/process_ans/', methods=['POST'])
def process_form(test_id):
    try:
        if request.method == 'POST':
            extension = None
            clean_files(100)
            file = request.files.get('photo')
            mode = request.form.get('model')

            if '.' in file.filename:
                extension = file.filename.rsplit('.', 1)[1]
            else:
                raise TypeError

            if file and is_extension_allowed(extension):
                file_name = 'image' + f'.{extension}'
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
                file.save(file_path)
                base64_txt = base64.b64encode(open(file_path, "rb").read())
                result = process_img(app.config["UPLOAD_FOLDER"], handwriting=bool(mode))
                os.remove(file_path)

                # database
                conn = sqlite3.connect('test.db')
                cursor = conn.cursor()

                cursor.execute("UPDATE alltest SET ans_img=?, ans_txt =? WHERE id=?;", [base64_txt, result, test_id])

                conn.commit()
                cursor.close()
                conn.close()

                return redirect(url_for('check_ans', test_id=test_id))
            else:
                raise TypeError

    except TypeError:
        return render_template('error.html', error_msg="type error while processing form")


@app.route('/tests/<test_id>/check_ans/', methods=['GET', 'POST'])
def check_ans(test_id):
    if request.method == 'GET':
        # database
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()

        cursor.execute("SELECT ans_txt, ans_img  FROM alltest WHERE id = ?;", [test_id])
        answer, image = cursor.fetchone()
        image = str(image)[2:-1]

        cursor.close()
        conn.close()

        # with open(f'{app.config["UPLOAD_FOLDER"]}/{test_id}/ans/outputs/ans.txt', 'r') as f:
        #     answer = f.read()
        return render_template('Answer/check.html', test_id=test_id, answer=answer, image=image)

    # post itself to change ans
    if request.method == 'POST':
        text = request.form.get("stu_ans")
        # database
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()

        cursor.execute("UPDATE alltest SET ans_txt =? WHERE id=?;", [text, test_id])

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('detail', test_id=test_id))


# View ans
@app.route('/tests/<test_id>/view_ans/', methods=['GET'])
def view_ans(test_id):
    # database
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    cursor.execute("SELECT ans_txt, ans_img  FROM alltest WHERE id = ?;", [test_id])
    answer, image = cursor.fetchone()
    image = str(image)[2:-1]

    cursor.close()
    conn.close()

    return render_template('Answer/view.html', test_id=test_id, answer=answer, image=image)


# #############################
# ####### Student Part ########
# #############################

# process student ans
@app.route('/tests/<test_id>/process_stu/', methods=['POST'])
def process_stu_form(test_id):
    try:
        if request.method == 'POST':
            extension = None
            clean_files(100)
            file = request.files.get('stu_ans')
            student_id = request.form.get('stu_id')
            mode = request.form.get('model')

            if '.' in file.filename:
                extension = file.filename.rsplit('.', 1)[1]
            else:
                raise TypeError

            if file and is_extension_allowed(extension):
                file_name = 'answer' + f'.{extension}'
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
                file.save(file_path)
                base64_txt = base64.b64encode(open(file_path, "rb").read())
                result = process_img(app.config["UPLOAD_FOLDER"], handwriting=bool(mode))
                os.remove(file_path)

                # database
                conn = sqlite3.connect('test.db')
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO allpaper (student_id, test_id, ans_img, ans_txt) VALUES (?, ?, ?, ?);",
                    [student_id, test_id, base64_txt, result])

                conn.commit()
                cursor.close()
                conn.close()

                return redirect(url_for('check_stu_ans', test_id=test_id, student_id=student_id))
            else:
                raise TypeError
    except TypeError:
        return render_template('error.html')


@app.route('/tests/<test_id>/<student_id>/check_ans', methods=['GET', 'POST'])
def check_stu_ans(test_id, student_id):
    if request.method == 'GET':
        # database
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()

        cursor.execute("SELECT ans_img, ans_txt FROM allpaper WHERE student_id = ? AND test_id = ?;",
                       [student_id, test_id])
        image, answer = cursor.fetchone()
        image = str(image)[2:-1]

        cursor.close()
        conn.close()

        # with open(f'{app.config["UPLOAD_FOLDER"]}/{test_id}/ans/outputs/ans.txt', 'r') as f:
        #     answer = f.read()
        return render_template('Answer/check.html', test_id=test_id, answer=answer, image=image)

    # post itself to change ans
    if request.method == 'POST':
        text = request.form.get("stu_ans")
        # database
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()

        cursor.execute("UPDATE allpaper SET ans_txt =? WHERE student_id = ? AND test_id = ?;",
                       [text, student_id, test_id])

        conn.commit()
        cursor.close()
        conn.close()
        # TODO: should redirect to view stu detail here
        return redirect(url_for('detail', test_id=test_id))


# view detail
@app.route('/tests/<test_id>/<stu_name>/', methods=['GET'])
def stu_detail(test_id, stu_name):
    # Process Answer Image
    if request.method == 'GET':
        with open(f'{app.config["UPLOAD_FOLDER"]}/{test_id}/ans/outputs/ans.txt', 'r') as f:
            answer = f.read()
        with open(f'{app.config["UPLOAD_FOLDER"]}/{test_id}/students/{stu_name}/outputs/ans.txt', 'r') as f:
            stu_answer = f.read()
        details, correct, total = calculate(stu_answer, answer)
        return render_template('Student/result.html', test_id=test_id, stu_name=stu_name, detail=details,
                               correct=correct, total=total)

    return render_template('error.html')


# #############################
# ####### Scoring Part ########
# #############################

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
