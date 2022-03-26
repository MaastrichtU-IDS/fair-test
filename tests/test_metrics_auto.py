from fastapi.testclient import TestClient
from fair_test import FairTestAPI

# Test the API using the URL and expected score 
# defined with the test_test attribute for each metrics test

app = FairTestAPI(metrics_folder_path='example/metrics')

endpoint = TestClient(app)


def test_api():
    app.run_tests(endpoint)