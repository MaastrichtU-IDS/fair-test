### 📥 Install for development

Clone the repository and install the dependencies locally for development:

```bash
git clone https://github.com/MaastrichtU-IDS/fair-test
cd fair-test
pip install -e .
```

<details><summary>You can try to use a virtual environment to avoid conflicts, if you face issues</summary>

```bash
# Create the virtual environment folder in your workspace
python3 -m venv .venv
# Activate it using a script in the created folder
source .venv/bin/activate
```
</details>

### ✅ Run the tests

<details><summary>Install <code>pytest</code> for testing</summary>

```bash
pip install pytest
```
</details>

Run the tests locally (from the root folder) with prints displayed:

```bash
pytest -s
```

### 📖 Generate docs

Install the dependencies to generate documentation:

```bash
pip install "jinja2==3.0.3" "mkdocstrings[python]" "mkdocs-material"
```

Start the docs on [http://localhost:8000](http://localhost:8000)

```bash
mkdocs serve
```

