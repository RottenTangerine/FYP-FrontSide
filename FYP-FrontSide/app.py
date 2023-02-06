import base64
import os
import re
import uuid

from flask import Flask, render_template, redirect, url_for
from flask import request, send_from_directory

from upload import *

from process import *

app = Flask(__name__)
np.set_printoptions(threshold=np.inf)
np.set_printoptions(linewidth=1500)

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
@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    img_url = None
    extension = None
    if request.method == 'POST':
        file = request.files.get('photo')

        if '.' in file.filename:
            extension = file.filename.rsplit('.', 1)[1]

        if file and is_extension_allowed(extension):
            file_name = str(uuid.uuid1()) + f'.{extension}'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            img_url = url_for('uploaded', filename=file_name)
    return f'You Upload an Image {img_url}'


# Get Image
@app.route('/uploaded/<filename>')
def uploaded(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Process Image

# Show Result


if __name__ == '__main__':
    app.run(debug=True)
    app.jinja_env.auto_reload = True
