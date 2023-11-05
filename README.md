# fm2svg
Feature Model to SVG Converter

`docker build -t fm2svg .`
`docker run fm2svg`

`curl -X POST http://127.0.0.1:5000/ -F file=@model.xml -o "model.svg"`