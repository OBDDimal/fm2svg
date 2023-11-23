# fm2svg
Feature Model to SVG Converter

`docker build -t fm2svg .`

`docker run -p 5000:5000 fm2svg`

`curl -X POST http://172.17.0.2:5000/download -F xml=@model.xml -F json=@model -o "model.svg"`

`http://172.17.0.2:5000`