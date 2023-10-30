import tempfile
from os import path, urandom
from flask import Flask, flash, request, Response, jsonify, render_template
from selenium.webdriver.common.by import By

from werkzeug.utils import secure_filename

from selenium import webdriver

import json
import xmltodict

from pprint import pprint

# -----------------------------------------------------------------------------

UPLOAD_FOLDER = '/tmp/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = urandom(32)


# -----------------------------------------------------------------------------

@app.route('/ping', methods=["GET", "POST"])
def index():
    return Response("Running...", status=200)


@app.route('/render', methods=["GET"])
def render():
    # TODO: Read JSON from payload
    # TODO: JSON + D3 (Jinja2)

    # with tempfile.NamedTemporaryFile() as ntf:
    #     with open(ntf, "w+") as file:
    #         file.write(render_template("index.html", title="test"))
    #
    #     content = downloadSVG(ntf)
    #
    # return Response(content, status=200)

    return render_template("index.html", title="test")


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

    # TODO: XML -> JSON
    with open(filepath, "r") as file:
        raw = file.read()

    xml_data = xmltodict.parse(raw, process_namespaces=True)

    struct = xml_data["featureModel"]["struct"]
    json_data = json.dumps(struct, indent=4)

    pprint(json_data)

    # TODO: JSON as payload
    svg = downloadSVG("localhost:5000/render")

    return Response(svg, status=200)


# TODO: on get request -> Upload button

def downloadSVG(sourceFile):
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.get(sourceFile)

    svg = driver.find_element(by=By.TAG_NAME, value="svg").get_attribute("innerHTML")
    style = driver.find_element(by=By.TAG_NAME, value="style").get_attribute("outerHTML")

    driver.quit()

    final_content = "<svg preserveaspectratio=\"xMidYMid meet\" viewbox=\"0 0 1850 496\">" + style + svg + "</svg>"

    return final_content
