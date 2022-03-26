FROM python:3.9

WORKDIR /app

# ADD requirements.txt .
# RUN pip install -r requirements.txt

ADD . .
# RUN pip install .

RUN pip install "jinja2==3.0.3" "mkdocstrings[python]" "mkdocs-material"

ENTRYPOINT [ "mkdocs", "serve", "-a", "0.0.0.0:8000" ]