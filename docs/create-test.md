This page explains how to create a FAIR metrics tests.

## 🎯 Define a FAIR metrics test

Create a file in the `metrics` folder with your test. Here is a basic example, with explanatory comments, to check if RDF metadata can be found at the subject URI:

````python title="metrics/a1_check_something.py"
from fair_test import FairTest, FairTestEvaluation

class MetricTest(FairTest):
    # Define the parameters of the tests
    metric_path = 'a1-check-something'
    applies_to_principle = 'A1'
    title = 'Check something'
    description = """Test something"""
    # Optional, will use contact infos from the .env file if not provided here
    author = 'https://orcid.org/0000-0000-0000-0000'
    contact_url="https://github.com/LUMC-BioSemantics/RD-FAIRmetrics"
    contact_name="Your Name"
    contact_email="your.email@email.com"
    organization="The Organization for which this test is published"
    # Optional, if your metric test has a detailed readme:
    metric_readme_url="https://w3id.org/rd-fairmetrics/RD-F4"

    metric_version = '0.1.0'
    # You can provide a list of URLs to automatically test
    # And the score the test is expected to compute
    test_test={
        'https://w3id.org/fair-enough/collections': 1,
        'http://example.com': 0,
    }

    # Define the function to evaluate
    def evaluate(self, eval: FairTestEvaluation):
        # Use the eval object to get the subject of the evaluation
        # Or access most functions needed for the evaluation (logs, fail, success)
        eval.info(f'Checking something for {eval.subject}')
        g = eval.retrieve_metadata(eval.subject, use_harvester=False)
        if len(g) > 0:
            eval.success(f'{len(g)} triples found, test sucessful')
        else:
            eval.failure('No triples found, test failed')
        return eval.response()
````

ℹ️ A few common operations are available on the `eval` object (a `FairTestEvaluation`):

* **Logging** operations:
```python
eval.info('Something happened')
eval.warn('Something bad happened')
eval.failure('The test failed')
eval.success('The test succeeded')
```

* **Retrieve metadata** from a URL (returns a RDFLib Graph, or JSON-like object):

```python
g = eval.retrieve_metadata(eval.subject)
```

!!! tip "Improve the metadata harvesting workflow"

	If the `retrieve_metadata()` function is missing some use-cases, and you would like to improve it, you can find the code in the [`fair_test/fair_test_evaluation.py`](https://github.com/MaastrichtU-IDS/fair-test/blob/main/fair_test/fair_test_evaluation.py#L112) file. Checkout the [Contribute page](/fair-test/contributing) to see how to edit the `fair-test` library.

* Parse a **string to RDF**:

```python
g = eval.parse_rdf(text,
    mime_type='text/turtle',
    log_msg='RDF from the subject URL'
)
```

* Return the metric test **results**:

```python
return eval.response()
```

* There is also a dictionary `test_test` to define URIs to be **automatically tested** against each metric, and the expected score. See the [Development workflow](/fair-test/development-workflow) page for more detail on running the tests.

!!! abstract "Documentation for all functions"

    You can find the details for all functions available in the [Code reference](/fair-test/FairTestEvaluation) section


## 🥷 Use secrets

You can also securely provide secrets environment variables

It can be useful to pass API keys to use private services in your metrics tests, such as Search engines APIs. In this example we will define an API key to perform Bing search named `APIKEY_BING_SEARCH`

1. Create an additional `secrets.env` environment file, it should not be committed to git (make sure it is added to the `.gitignore`).

    ```bash title="secrets.env"
    APIKEY_BING_SEARCH=yourapikey
    ```

2. To use the secret in development define the env variable locally in your terminal with:

    ```bash
    export APIKEY_BING_SEARCH="yourapikey"
    ```

3. Add this file to your `docker-compose.yml` to use the secrets in production:

    ```yaml title="docker-compose.yml"
    services:
        api:
            env_file:
            - secrets.env
    ```

4. You can then retrieve this API key in your metrics tests:

    ```python title="metrics/a1_check_something.py"
    import os
    apikey = os.getenv('APIKEY_BING_SEARCH')
    ```
