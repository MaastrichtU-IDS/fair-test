This page explains how to create a FAIR metrics test API with `fair-test`.

## 📥 Install the package

Install the package from [PyPI](https://pypi.org/project/fair-test/){:target="_blank"}:

```bash
pip install fair-test
```


## 📝 Define the API

Create a `main.py` file to declare the API, you can provide a different folder than `metrics` here, the folder path is relative to where you start the API (the root of the repository):

```python title="main.py"
from fair_test import FairTestAPI

app = FairTestAPI(
    title='FAIR Metrics tests API',
    metrics_folder_path='metrics',
    description="""FAIR Metrics tests API""",
    cors_enabled=True,
    license_info = {
        "name": "MIT license",
        "url": "https://opensource.org/licenses/MIT"
    },
)
```

Create a `.env` file to provide informations used for the API, such as contact details and the host URL (note that you don't need to change it for localhost in development), e.g.:

```bash title=".env"
HOST_URL="https://metrics.api.fair-enough.semanticscience.org"
CONTACT_URL="https://github.com/MaastrichtU-IDS/fair-enough-metrics"
CONTACT_NAME="Vincent Emonet"
CONTACT_EMAIL="vincent.emonet@gmail.com"
CONTACT_ORCID="0000-0000-0000-0000"
ORG_NAME="Institute of Data Science at Maastricht University"
DEFAULT_SUBJECT="https://doi.org/10.1594/PANGAEA.908011"
```

## 🎯 Define a FAIR metrics test

Create a `a1_check_something.py` file in the `metrics` folder with your test:

````python title="metrics/a1_check_something.py"
from fair_test import FairTest

class MetricTest(FairTest):
    metric_path = 'a1-check-something'
    applies_to_principle = 'A1'
    title = 'Check something'
    description = """Test something"""
    author = 'https://orcid.org/0000-0000-0000-0000'
    metric_version = '0.1.0'
    test_test={
        'http://doi.org/10.1594/PANGAEA.908011': 1,
        'https://github.com/MaastrichtU-IDS/fair-test': 0,
    }

    def evaluate(self):
        self.info(f'Checking something for {self.subject}')
        g = self.retrieve_rdf(self.subject, use_harvester=False)
        if len(g) > 0:
            self.success(f'{len(g)} triples found, test sucessful')
        else:
            self.failure('No triples found, test failed')
        return self.response()
````

ℹ️ A few common operations are available on the `self` object:

* Logging operations: 
```python
self.info('Something happened')
self.warn('Something bad happened')
self.failure('The test failed')
self.success('The test succeeded')
```

* Retrieve RDF from a URL (returns a RDFLib Graph): 

```python
g = self.retrieve_rdf(self.subject)
```

* Parse a string to RDF:

```python
g = self.parse_rdf(text, 
    mime_type='text/turtle', 
    log_msg='RDF from the subject URL'
)
```

* Return the metric test results:

```python
return self.response()
```

## 🦄 Deploy the API

You can then run the metrics tests API using `uvicorn`.

!!! example "Example"

	For example you can get started with the code provided in the  [`example` folder](https://github.com/MaastrichtU-IDS/fair-test/tree/main/example){:target="_blank"}, check the `example/README.md` for more options, such as deploying it with docker.

Go to the FAIR metrics API folder, and install the requirements:

```bash
cd example
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn main:app --reload
```

You can now access the FAIR Test API on [http://localhost:8000](http://localhost:8000){:target="_blank"} and try to run your test using the `POST` request, or  get its descriptive metadata with the `GET` request.
