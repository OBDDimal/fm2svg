import logging
import os
import tempfile
import re
from os import path, urandom

from pyvirtualdisplay import Display
from flask import Flask, flash, request, Response, render_template, json
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


@app.route('/', methods=["GET", "POST"])
def render():
    if request.method == 'POST':
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

        return render_template("fmviewer.html", xml=raw)
    else:
        return render_template("index.html")


@app.route('/download', methods=["POST"])
def upload():
    if request.method == 'POST':
        if "xml" not in request.files:
            flash("no file supplied")
            return Response("no file supplied", status=422)

        # handle xml
        xml = request.files["xml"]

        if not xml or xml.filename == "":
            return Response("no file supplied", status=422)

        filename = secure_filename(xml.filename)
        filepath = path.join(UPLOAD_FOLDER, filename)
        xml.save(filepath)

        with open(filepath, "r") as file:
            raw_xml = file.read()

        # handle json
        if "json" in request.files:
            json = request.files["json"]

            if not json or json.filename == "":
                raw_json = ""
            else:
                filename = secure_filename(json.filename)
                filepath = path.join(UPLOAD_FOLDER, filename)
                json.save(filepath)

                with open(filepath, "r") as file:
                    raw_json = file.read()
        else:
            raw_json = ""

        with tempfile.NamedTemporaryFile(suffix=".html") as ntf:
            with open(ntf.name, "w+") as file:
                file.write(render_template("fmviewer.html", xml=raw_xml, json_data=raw_json))

            content = download_svg("file://" + ntf.name)

        return Response(content, status=200)
    else:
        return render_template("index.html")


# TODO: on get request -> Upload button

def download_svg(source_file):
    # ---

    display = Display(visible=0, size=(800, 600))
    display.start()

    options = webdriver.FirefoxOptions()
    options.binary_location = r'/opt/firefox/'
    options.headless = True

    # ---

    driver = webdriver.Firefox(options=options)

    driver.implicitly_wait(10)
    driver.get(source_file)

    svg = driver.find_element(by=By.TAG_NAME, value="svg").get_attribute("innerHTML")
    svg_outer_html = driver.find_element(by=By.TAG_NAME, value="svg").get_attribute("outerHTML")
    viewbox = re.search('viewBox="[0-9]* [0-9]* [0-9]* [0-9]*"', svg_outer_html).group(0)
    style = driver.find_element(by=By.TAG_NAME, value="style").get_attribute("outerHTML")

    driver.quit()
    display.stop()

    final_content = ("<svg preserveAspectRatio=\"xMidYMid meet\" " + viewbox + " version=\"1.1\" "
                     + "xmlns=\"http://www.w3.org/2000/svg\">" + style + svg + "</svg>")

    return final_content


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
