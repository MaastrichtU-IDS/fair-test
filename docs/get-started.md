This page guides you to choose where and how to create your FAIR tests.

## ♻️ Use an existing FAIR test repository

You are welcome to submit a pull request to propose to add your tests to our API in production: [https://metrics.api.fair-enough.semanticscience.org](https://metrics.api.fair-enough.semanticscience.org){:target="_blank"}

1. Fork the repository [https://github.com/MaastrichtU-IDS/fair-enough-metrics](https://github.com/MaastrichtU-IDS/fair-enough-metrics){:target="_blank"}
2. Clone your forked repository
3. Checkout the `README.md` to run it in development
4. Send us a pull request to integrate your test to our API at {{cookiecutter.host_url}}
5. Once your test is published, register it in existing FAIR evaluation services (cf. the [publish page](/fair-test/publish/#then-register-your-tests){:target="_blank"}.

## 📂 Create a new repository for your tests

### 🍪 With the cookiecutter interactive CLI

Install [cookiecutter](https://github.com/cookiecutter/cookiecutter){:target="_blank"}:

```bash
pip install cookiecutter
```

Initialize your FAIR tests repository using the interactive CLI:

```bash
cookiecutter https://github.com/vemonet/cookiecutter-fair-test
```

Check the generated `README.md` for more details on how to deploy the API in production or run the tests.

### ✍️ Manually

1. Create a `pyproject.toml` file:

    ```toml title="pyproject.toml"
    [project]
    version = "0.1.0"
    name = "My FAIR test API"
    description = "Implementation of the FAIR metrics tests for..."
    readme = "README.md"
    requires-python = ">=3.9"
    license = { file = "LICENSE" }
    authors = [
        { name = "Firstname Lastname", email = "firstname.lastname@example.com" },
    ]
    dependencies = [
        "fair-test >=0.0.7",
    ]

    [project.optional-dependencies]
    test = [
        "pytest >=7.1.3,<8.0.0",
    ]
    dev = [
        "uvicorn[standard] >=0.12.0,<0.19.0",
    ]
    ```

2. Define the API: create a `main.py` file to declare the API, you can provide a different folder than `metrics` here, the folder path is relative to where you start the API (the root of the repository):

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

3. Create a `.env` file to provide the global informations used for the API, such as contact details and the host URL (note that you don't need to change it for localhost in development), e.g.:

    ```bash title=".env"
    HOST_URL="https://metrics.api.fair-enough.semanticscience.org"
    CONTACT_URL="https://github.com/MaastrichtU-IDS/fair-enough-metrics"
    CONTACT_NAME="Firstname Lastname"
    CONTACT_EMAIL="firstname.lastname@example.com"
    CONTACT_ORCID="0000-0000-0000-0000"
    ORG_NAME="Affiliation"
    DEFAULT_SUBJECT="https://doi.org/10.1594/PANGAEA.908011"
    ```
