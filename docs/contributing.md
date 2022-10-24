This page details the workflow to contribute to the `fair-test` library.

[![Version](https://img.shields.io/pypi/v/fair-test)](https://pypi.org/project/fair-test) [![Python versions](https://img.shields.io/pypi/pyversions/fair-test)](https://pypi.org/project/fair-test) [![Pull requests welcome](https://img.shields.io/badge/pull%20requests-welcome-brightgreen)](https://github.com/MaastrichtU-IDS/fair-test/fork)

[![Run tests](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/test.yml/badge.svg)](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/test.yml) [![CodeQL](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/codeql-analysis.yml) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=MaastrichtU-IDS_fair-test&metric=coverage)](https://sonarcloud.io/dashboard?id=MaastrichtU-IDS_fair-test)

[![Publish to PyPI](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/publish.yml/badge.svg)](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/publish.yml) [![Publish docs](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/deploy-docs.yml/badge.svg)](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/deploy-docs.yml)

## 📥 Install for development

Clone the repository and go in the project folder:

```bash
git clone https://github.com/MaastrichtU-IDS/fair-test
cd fair-test
```

To install the project for development you can either use [`venv`](https://docs.python.org/3/library/venv.html) to create a virtual environment yourself, or use [`hatch`](https://hatch.pypa.io) to automatically handle virtual environments for you.

=== "venv"

    Create the virtual environment in the project folder :

    ```bash
    python3 -m venv .venv
    ```

    Activate the virtual environment:

    ```bash
    source .venv/bin/activate
    ```

    Install all dependencies required for development:

    ```bash
    pip install -e ".[dev,doc,test]"
    ```

    You can also enable automated formatting of the code at each commit:

    ```bash
    pre-commit install
    ```

=== "hatch"

    Install [Hatch](https://hatch.pypa.io), this will automatically handle virtual environments and make sure all dependencies are installed when you run a script in the project:

    ```bash
    pip install hatch
    ```

    ??? note "Optionally you can improve `hatch` terminal completion"

        See the [official documentation](https://hatch.pypa.io/latest/cli/about/#tab-completion) for more details. For ZSH you can run these commands:

        ```bash
        _HATCH_COMPLETE=zsh_source hatch > ~/.hatch-complete.zsh
        echo ". ~/.hatch-complete.zsh" >> ~/.zshrc
        ```


## 🧑‍💻 Development workflow

=== "venv"

    Deploy the FAIR test API defined in the `example` folder to test your changes:

    ```bash
    ./scripts/dev.sh
    ```

    The code will be automatically formatted when you commit your changes using `pre-commit`. But you can also run the script to format the code yourself:

    ```bash
    ./scripts/format.sh
    ```

    Or check the code for errors:

    ```bash
    ./scripts/lint.sh
    ```

=== "hatch"

    Deploy the FAIR test API defined in the `example` folder to test your changes:

    ```bash
    hatch run dev
    ```

    The code will be automatically formatted when you commit your changes using `pre-commit`. But you can also run the script to format the code yourself:

    ```bash
    hatch run format
    ```

    Or check the code for errors:

    ```bash
    hatch run lint
    ```


## ✅ Run the tests

[![Run tests](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/test.yml/badge.svg)](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/test.yml) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=MaastrichtU-IDS_fair-test&metric=coverage)](https://sonarcloud.io/dashboard?id=MaastrichtU-IDS_fair-test)

Tests are automatically run by a GitHub Actions workflow when new code is pushed to the GitHub repository. The subject URLs to test and their expected score are retrieved from the `test_test` attribute for each metric test.??? success "Install pytest for testing"

??? note "If not already done, define the 2 files required to run the tests"

    It will test all cases defined in your FAIR metrics tests `test_test` attributes:

    ```python title="tests/conftest.py"
    def pytest_addoption(parser):
        parser.addoption("--metric", action="store", default=None)
    ```

    and:

    ```python title="tests/test_metrics.py"
    import pytest
    from fastapi.testclient import TestClient
    from main import app

    endpoint = TestClient(app)

    def test_api(pytestconfig):
        app.run_tests(endpoint, pytestconfig.getoption('metric'))
    ```


=== "venv"

	Run the tests locally:

	```bash
	./scripts/test.sh
	```

	You can also run the tests only for a specific metric test:

	```bash
	./scripts/test.sh --metric a1-metadata-protocol
	```

=== "hatch"

	Run the tests locally:

	```bash
	hatch run test
	```

	You can also run the tests only for a specific metric test:

	```bash
	hatch run test --metric a1-metadata-protocol
	```


## 📖 Generate docs

[![Publish docs](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/deploy-docs.yml/badge.svg)](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/deploy-docs.yml)

The documentation (this website) is automatically generated from the markdown files in the `docs` folder and python docstring comments, and published by a GitHub Actions workflow.

Serve the docs on [http://localhost:8008](http://localhost:8008){:target="_blank"}

=== "venv"

    ```bash
    ./scripts/docs-serve.sh
    ```

=== "hatch"

    ```bash
    hatch run docs
    ```


## 🏷️ Publish a new release

[![Publish to PyPI](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/publish.yml/badge.svg)](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/publish.yml)

1. Increment the `__version__` in `fair_test/__init__.py`
2. Push to GitHub
3. Create a new release on GitHub
4. A GitHub Action workflow will automatically publish the new version to PyPI

<!--

## 🐣 Hatch development workflow

Install [Hatch](https://hatch.pypa.io), this will automatically handle virtual environments and make sure all dependencies are installed when you run a script in the project:

```bash
pip install hatch
```

??? note "Optionally you can improve `hatch` terminal completion"

    See the [official documentation](https://hatch.pypa.io/latest/cli/about/#tab-completion) for more details. For ZSH you can run these commands:

    ```bash
    _HATCH_COMPLETE=zsh_source hatch > ~/.hatch-complete.zsh
    echo ". ~/.hatch-complete.zsh" >> ~/.zshrc
    ```

Deploy the FAIR test API defined in the `example` folder to test your changes:

```bash
hatch run dev
```

Format the code automatically:

```bash
hatch run format
```

Automatically check the code for errors:

```bash
hatch run lint
```

Serve the docs locally:

```bash
hatch run docs
```

Run the tests:

```bash
hatch run test
```
-->
