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

Create a `.env` file to provide the global informations used for the API, such as contact details and the host URL (note that you don't need to change it for localhost in development), e.g.:

```bash title=".env"
HOST_URL="https://metrics.api.fair-enough.semanticscience.org"
CONTACT_URL="https://github.com/MaastrichtU-IDS/fair-enough-metrics"
CONTACT_NAME="Vincent Emonet"
CONTACT_EMAIL="vincent.emonet@gmail.com"
CONTACT_ORCID="0000-0000-0000-0000"
ORG_NAME="Institute of Data Science at Maastricht University"
DEFAULT_SUBJECT="https://doi.org/10.1594/PANGAEA.908011"
```


??? note "You can also securely provide secrets environment variables"

    It can be useful to pass API keys to use private services in your metrics tests, such as Search engines APIs. In this example we will define an API key to perform Bing search named `APIKEY_BING_SEARCH`
    
    1. Create an additional `secrets.env` environment file, it should not be committed to git (make sure it is added to the `.gitignore`).
    
        ```bash title="secrets.env"
        APIKEY_BING_SEARCH=yourapikey
        ```
    
    2. Add this file to your `docker-compose.prod.yml` to use the secrets in production:
    
        ```yaml title="docker-compose.prod.yml"
        services:
            api:
                env_file:
                - secrets.env
        ```
    
        To use the secret in development you can also add it to the `docker-compose.yml`, or define the env variable locally in your terminal with `export APIKEY_BING_SEARCH="yourapikey"`. But be careful not blowing up your quotas.
    
    3. You can then retrieve this API key in your metrics tests:
    
        ```python title="metrics/a1_check_something.py"
        import os
        apikey = os.getenv('APIKEY_BING_SEARCH')
        ```

## 🎯 Define a FAIR metrics test

Create a `a1_check_something.py` file in the `metrics` folder with your test:

````python title="metrics/a1_check_something.py"
from fair_test import FairTest, FairTestEvaluation

class MetricTest(FairTest):
    metric_path = 'a1-check-something'
    applies_to_principle = 'A1'
    title = 'Check something'
    description = """Test something"""
    # Optional, infos about contacts will be defined by the .env file if not provided here
    author = 'https://orcid.org/0000-0000-0000-0000'
    contact_url="https://github.com/LUMC-BioSemantics/RD-FAIRmetrics"
    contact_name="Your Name"
    contact_email="your.email@email.com"
    organization="The Organization for which this test is published"
    # Optional, if your metric test has a detailed readme:
    metric_readme_url="https://w3id.org/rd-fairmetrics/RD-F4"
    
    metric_version = '0.1.0'
    test_test={
        'https://w3id.org/fair-enough/collections': 1,
        'http://example.com': 0,
    }

    
    def evaluate(self, eval: FairTestEvaluation):
        eval.info(f'Checking something for {self.subject}')
        g = eval.retrieve_metadata(self.subject, use_harvester=False)
        if len(g) > 0:
            eval.success(f'{len(g)} triples found, test sucessful')
        else:
            eval.failure('No triples found, test failed')
        return eval.response()
````

ℹ️ A few common operations are available on the `self` object:

* Logging operations: 
```python
eval.info('Something happened')
eval.warn('Something bad happened')
eval.failure('The test failed')
eval.success('The test succeeded')
```

* Retrieve RDF from a URL (returns a RDFLib Graph): 

```python
g = eval.retrieve_metadata(eval.subject)
```

* Parse a string to RDF:

```python
g = eval.parse_rdf(text, 
    mime_type='text/turtle', 
    log_msg='RDF from the subject URL'
)
```

* Return the metric test results:

```python
return eval.response()
```

* There is also a dictionary `test_test` to define URIs to be automatically tested against each metric, and the expected score. See the [Development](/fair-test/development) section for more detail on running the tests.

!!! abstract "Documentation for all functions"

    You can find the details for all functions available in the [Code reference](/fair-test/FairTestEvaluation) section


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
