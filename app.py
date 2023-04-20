from flask import Flask, render_template, redirect, url_for, send_file
from flask import request

import os
import base64
import collections

import pandas as pd
import sqlite3

from icecream import ic

from process import process_img
from upload import *
from result import *

app = Flask(__name__)

# config
# save location
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'temporary')
# file size constraint
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 8  # TODO: not works (future work)


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
    # get the test ans
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ans_txt FROM alltest WHERE id = ?;", [test_id])
    answer = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    paper_meta = None
    score_counter = None
    status_counter = None
    correct_detail_by_group = None
    wrong_detail_by_group = None

    # get all papers' metadata of the test
    conn = sqlite3.connect('test.db')
    tests_df = pd.read_sql('SELECT * FROM allpaper', conn)
    conn.close()

    # ic(tests_df)

    if not tests_df.empty:
        # find all answers for this test
        paper_meta = tests_df[['student_id', 'status', 'ans_txt', 'test_id']]
        paper_meta = paper_meta[paper_meta['test_id'] == int(test_id)]

        if not paper_meta.empty:
            paper_meta["result"] = paper_meta["ans_txt"].apply(lambda x: calculate(x, answer)[1:])
            # split the result column into two columns score and total
            paper_meta[["detail", "score", "total"]] = pd.DataFrame(paper_meta["result"].tolist(),
                                                                    index=paper_meta.index)
            # ic(paper_meta)
            # drop the result column
            paper_meta.drop("result", axis=1, inplace=True)

            # Data for student status pie chart
            status_dist_data = paper_meta['status'].values.tolist()
            status_counter = dict(collections.Counter(status_dist_data))
            # ic(status_dist_data, status_counter)

            # Data for Each question
            question_detail = pd.DataFrame(paper_meta['detail'].tolist())
            question_detail['status'] = paper_meta['status'].reset_index(drop=True)
            paper_meta.drop("detail", axis=1, inplace=True)
            ic(question_detail)

            correct_detail_by_group = question_detail.groupby('status').sum()
            total_detail_by_group = question_detail.groupby('status').count()
            wrong_detail_by_group = total_detail_by_group - correct_detail_by_group

            correct_detail_by_group = correct_detail_by_group.values.tolist()
            wrong_detail_by_group = wrong_detail_by_group.values.tolist()

            # Data for student score distribution bar chart
            score_dist_data = paper_meta['score'].values.tolist()
            ic(correct_detail_by_group, wrong_detail_by_group)
            ic(paper_meta)
            score_counter = collections.Counter(score_dist_data)
            score_counter = {int(k): v for k, v in score_counter.items()}
            for i in range(len(correct_detail_by_group) + 1):
                if i in score_counter.keys():
                    continue
                score_counter[i] = 0
            ic(score_dist_data, score_counter)

            # student_details paper meta columns: ['student_id', 'status', 'ans_txt', 'test_id', 'score', 'total']
            paper_meta = paper_meta.values
        else:
            paper_meta = None
    return render_template('Test/detail.html', student_details=paper_meta, have_ans=answer is not None,
                           test_id=test_id, score_counter=score_counter, status_counter=status_counter,
                           correct_detail_by_group=correct_detail_by_group, wrong_detail_by_group=wrong_detail_by_group)


@app.route('/test/<test_id>/delete/', methods=['GET'])
def delete_test(test_id):
    # connect database
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM alltest WHERE id = ?;", [test_id])
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('index'))


# ############################
# ####### Answer Part ########
# ############################

@app.route('/tests/<test_id>/process_ans/', methods=['POST'])
def process_form(test_id):
    try:
        if request.method == 'POST':
            extension = None
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
                result = process_img(file_path, handwriting=bool(mode))
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
    status_dict = {
        '1': 'OK',
        '2': 'Late Submission',
        '3': 'Cheat',
    }

    try:
        if request.method == 'POST':
            extension = None
            file = request.files.get('stu_ans')
            student_id = request.form.get('stu_id')
            status = request.form.get('status')
            ic(status)

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
                result = process_img(file_path, handwriting=bool(mode))
                os.remove(file_path)

                # database
                conn = sqlite3.connect('test.db')
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO allpaper (student_id, test_id, status, ans_img, ans_txt) VALUES (?, ?, ?, ?, ?);",
                    [student_id, test_id, status_dict[status], base64_txt, result])

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

        return render_template('Student/check.html', test_id=test_id, student_id=student_id, answer=answer, image=image)

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
        return redirect(url_for('result', test_id=test_id, student_id=student_id))


@app.route('/tests/<test_id>/<student_id>/view_ans/', methods=['GET'])
def view_stu_ans(test_id, student_id):
    # database
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    cursor.execute("SELECT ans_txt, ans_img  FROM allpaper WHERE student_id = ? AND test_id = ?;",
                   [student_id, test_id])
    answer, image = cursor.fetchone()
    image = str(image)[2:-1]

    cursor.close()
    conn.close()

    return render_template('Student/view.html', test_id=test_id, student_id=student_id, answer=answer, image=image)


@app.route('/test/<test_id>/<student_id>/delete/', methods=['GET'])
def delete_stu_ans(test_id, student_id):
    # connect database
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM allpaper WHERE test_id = ? and student_id = ?;", [test_id, student_id])
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('detail', test_id=test_id))


# #############################
# ####### Scoring Part ########
# #############################

# Show Result
@app.route('/tests/<test_id>/<student_id>/results/')
def result(test_id, student_id):
    # database
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    cursor.execute("SELECT ans_txt FROM alltest WHERE id = ?;",
                   [test_id])
    ans = cursor.fetchone()[0]
    cursor.execute("SELECT ans_txt FROM allpaper WHERE student_id = ? AND test_id = ?;",
                   [student_id, test_id])
    stu_ans = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    info, result, correct, total = calculate(stu_ans, ans)

    return render_template('Student/result.html', test_id=test_id, result=result, info=info, correct=correct,
                           total=total)


@app.route('/download')
def download_file():
    path = "export.zip"
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
    app.jinja_env.auto_reload = True
