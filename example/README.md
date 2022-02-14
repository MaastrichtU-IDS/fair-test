# Example FAIR test API

A FAIR metrics tests service supporting the specifications used by the [FAIRMetrics working group](https://github.com/FAIRMetrics/Metrics).

Built in Python with [RDFLib](https://github.com/RDFLib/rdflib) and [FastAPI](https://fastapi.tiangolo.com/), CORS enabled.

## Install and run ✨️

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Run the server on http://localhost:8000

```bash
uvicorn main:app --reload
```

## Or run with docker 🐳

Checkout the `Dockerfile` to see how the image is built, and run it with the `docker-compose.yml`:

```bash
docker-compose up -d --build
```

Or build and run with docker:

```bash
docker build -t fair-test .
```

Run on http://localhost:8000

```bash
docker run -p 8000:80 fair-test
```

