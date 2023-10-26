import os
from os import path, urandom
from flask import Flask, flash, request, Response, jsonify
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


@app.route('/downloadTest', methods=["GET"])
def download():
    sourcefile = "file://" + os.getcwd() + "/index.html"
    svg = downloadSVG(sourcefile, "")
    return Response(svg, status=200)

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

    # TODO: JSON + D3 (Jinja2)
    # TODO: Call Selenium to render to SVG
    sourcefile = "file://" + os.getcwd() + "/index.html"
    downloadSVG(sourcefile, "")

    return Response("Done", status=200)


# TODO: on get request -> Upload button

# TODO: Call Selenium to render to SVG
def downloadSVG(sourceFile, targetFile):
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.get(sourceFile)

    svg = driver.find_element(by=By.TAG_NAME, value="svg").get_attribute("innerHTML")
    style = driver.find_element(by=By.TAG_NAME, value="style").get_attribute("outerHTML")

    driver.quit()

    final_content = "<svg>" + style + svg + "</svg>"

    return final_content
