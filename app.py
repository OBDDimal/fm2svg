import os
import tempfile
import re
from os import path, urandom
from flask import Flask, flash, request, Response, jsonify, render_template
from selenium.webdriver.common.by import By

from werkzeug.utils import secure_filename

from selenium import webdriver

# -----------------------------------------------------------------------------

UPLOAD_FOLDER = '/tmp/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = urandom(32)


# -----------------------------------------------------------------------------

@app.route('/ping', methods=["GET", "POST"])
def index():
    return Response("Running...", status=200)


@app.route('/', methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("no file supplied")
        return Response("no file supplied", status=422)

    file = request.files["file"]

    if not file or file.filename == "":
        return Response("no file supplied", status=422)

    filename = secure_filename(file.filename)
    filepath = path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    with open(filepath, "r") as file:
        raw = file.read()

    with tempfile.NamedTemporaryFile(suffix=".html") as ntf:
        with open(ntf.name, "w+") as file:
            file.write(render_template("index.html", xml=raw))

        content = download_svg("file://" + ntf.name)

    return Response(content, status=200)


# TODO: on get request -> Upload button

def download_svg(source_file):
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.get(source_file)

    svg = driver.find_element(by=By.TAG_NAME, value="svg").get_attribute("innerHTML")
    svg_outer_html = driver.find_element(by=By.TAG_NAME, value="svg").get_attribute("outerHTML")
    viewbox = re.search('viewBox="[0-9]* [0-9]* [0-9]* [0-9]*"', svg_outer_html).group(0)
    style = driver.find_element(by=By.TAG_NAME, value="style").get_attribute("outerHTML")

    driver.quit()

    final_content = ("<svg preserveAspectRatio=\"xMidYMid meet\" " + viewbox + " version=\"1.1\" "
                     + "xmlns=\"http://www.w3.org/2000/svg\">" + style + svg + "</svg>")

    return final_content


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
