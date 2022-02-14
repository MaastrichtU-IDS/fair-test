# ☑️ FAIR testing API

[![Version](https://img.shields.io/pypi/v/fair-test)](https://pypi.org/project/fair-test) [![Python versions](https://img.shields.io/pypi/pyversions/fair-test)](https://pypi.org/project/fair-test)

[![Run tests](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/run-tests.yml/badge.svg)](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/run-tests.yml) [![Publish to PyPI](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/publish-package.yml/badge.svg)](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/publish-package.yml) [![CodeQL](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/codeql-analysis.yml) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=MaastrichtU-IDS_fair-test&metric=coverage)](https://sonarcloud.io/dashboard?id=MaastrichtU-IDS_fair-test)

`fair-test` is a library to build and deploy FAIR metrics tests APIs supporting the specifications used by the [FAIRMetrics working group](https://github.com/FAIRMetrics/Metrics), in Python.

It aims to enable python developers to easily write and deploy FAIR metric tests functions that can be queried by multiple FAIR evaluations services, such as [FAIR enough](https://fair-enough.semanticscience.org/) and the [FAIRsharing FAIR Evaluator](https://fairsharing.github.io/FAIR-Evaluator-FrontEnd/)

> Feel free to create an [issue](/issues), or send a pull request if you are facing issues or would like to see a feature implemented.

## 🧑‍🏫 How it works

The user defines and registers custom FAIR metrics tests in separated files in a specific folder (the `metrics` folder by default), and start the API.

The endpoint is CORS enabled by default.

Built with [RDFLib](https://github.com/RDFLib/rdflib) and [FastAPI](https://fastapi.tiangolo.com/). Tested for Python 3.7, 3.8 and 3.9

## 📥 Install the package

Install the package from [PyPI](https://pypi.org/project/fair-test/):

```bash
pip install fair-test
```

## 🐍 Build a FAIR metrics test API

Checkout the [`example`](https://github.com/MaastrichtU-IDS/fair-test/tree/main/example) folder for a complete working app example to get started, including a docker deployment. A good way to create a new FAIR testing API is to copy this `example` folder, and start from it.

### 📝 Define the API

Create a `main.py` file to declare the API:

```python
from fair_test import FairTestAPI, settings

app = FairTestAPI(
    title='FAIR Metrics tests API',
    metrics_folder_path='metrics',
    description="""FAIR Metrics tests API""",
    license_info = {
        "name": "MIT license",
        "url": "https://opensource.org/licenses/MIT"
    },
)
```

Create a `.env` file to provide informations used for the API, such as contact and host URL, e.g.:

```bash
HOST="metrics.api.fair-enough.semanticscience.org"
BASE_URI="https://metrics.api.fair-enough.semanticscience.org"
CONTACT_URL="https://github.com/MaastrichtU-IDS/fair-enough-metrics"
CONTACT_NAME="Vincent Emonet"
CONTACT_EMAIL="vincent.emonet@gmail.com"
CONTACT_ORCID="0000-0002-1501-1082"
ORG_NAME="Institute of Data Science at Maastricht University"
DEFAULT_SUBJECT="https://doi.org/10.1594/PANGAEA.908011"
```

### 📝 Define a FAIR metrics test

Create a `metrics/a1_my_test.py` file in your project folder with your custom metrics test:

````python
from api.metrics_test import FairTest

class MetricTest(FairTest):
    metric_path = 'a1-check-something'
    applies_to_principle = 'A1'
    title = 'Check something'
    description = """Test something"""
    author = 'https://orcid.org/0000-0000-0000-0000'
    metric_version = '0.1.0'

    def evaluate(self):
        self.info(f'Checking something for {self.subject}')
        g = self.getRDF(self.subject)
        if len(g) > 0:
            self.success(f'{len(g)} triples found, test sucessful')
        else:
            self.failure('No triples found, test failed')

        return self.response()
````

### 🦄 Deploy the API

You can then run the metrics tests API on http://localhost:8000/sparql with `uvicorn`

```bash
cd example
uvicorn main:app --reload
```

> Checkout in the `example/README.md` for more details, such as deploying it with docker.

## 🧑‍💻 Development

### 📥 Install for development

Clone and install locally for development:

```bash
git clone https://github.com/MaastrichtU-IDS/fair-test
cd fair-test
pip install -e .
```

You can use a virtual environment to avoid conflicts:

```bash
# Create the virtual environment folder in your workspace
python3 -m venv .venv
# Activate it using a script in the created folder
source .venv/bin/activate
```

### ✅️ Run the tests

Install additional dependencies for testing:

```bash
pip install pytest
```

Run the tests locally (from the root folder) and display prints:

```bash
pytest -s
```

## 📂 Projects using fair-test

Here are some projects using `fair-test` to deploy FAIR testing services:

* https://github.com/MaastrichtU-IDS/fair-enough-metrics
  * A generic  FAIR metrics tests service developed at the Institute of Data Science at Maastricht University.
* https://github.com/LUMC-BioSemantics/RD-FAIRmetric-F4
  * A FAIR metrics tests service for Rare Disease research.
