This page explains the usual development workflow used in FAIR tests repositories. It is recommended to also refer to the FAIR test repository README, when working in a specific repository.

## 📥️ Install dependencies

Create and activate a virtual environment if necessary:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies from the source code:

```bash
pip install -e ".[test,dev]"
```

## 🐍 Deploy the API in development

Start the API locally on [http://localhost:8000](http://localhost:8000){:target="_blank"}

```bash
uvicorn main:app --reload
```

> The API will automatically reload on changes to the code 🔄

## ✔️ Test the Metrics Tests API

The tests are run automatically by a GitHub Action workflow at every push to the `main` branch.

The subject URLs to test and their expected score are retrieved from the `test_test` attribute for each metric test.

Add tests in the `./tests/test_metrics.py` file. You just need to add new entries to the JSON file to test different subjects results against the metrics tests:

Run the tests locally (from the root folder):

```bash
pytest -s
```

Run the tests only for a specific metric test:

```bash
pytest -s --metric a1-metadata-protocol
```

## 🐳 Deploy with docker

From the root of the cloned repository, run the command below, and access the OpenAPI Swagger UI on [http://localhost:8000](http://localhost:8000){:target="_blank"}

```bash
docker-compose up
```

> You can use a reverse [nginx-proxy](https://github.com/nginx-proxy/nginx-proxy) for docker to route the services, or any other solution you want.

If you make changes to the dependencies in `pyproject.toml` you will need to rebuild the image to install the new requirements:

```bash
docker-compose up --build
```
