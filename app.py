from os import path, urandom
from flask import Flask, flash, request, Response, jsonify

from werkzeug.utils import secure_filename

# -----------------------------------------------------------------------------

UPLOAD_FOLDER = '/tmp/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = urandom(32)

# -----------------------------------------------------------------------------

@app.route('/ping', methods = ["GET", "POST"])
def index():
    return Response("Running...", status = 200)


@app.route('/', methods = ["POST"])
def upload():
    if "file" not in request.files:
        flash("no file supplied")
        return Response("no file supplied", status = 422)

    file = request.files["file"]

    if not file or file.filename == "":
        return Response("no file supplied", status = 422)

    filename = secure_filename(file.filename)
    filepath = path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    with open(filepath, "r") as file:
        print(file.read())

    # TODO: XML -> JSON
    # TODO: JSON + D3 (Jinja2)
    # TODO: Call Selenium to render to SVG

    return Response("Done", status = 200)
