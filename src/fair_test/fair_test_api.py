import os

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from fair_test.config import settings


class FairTestAPI(FastAPI):
    """
    Class to deploy a FAIR metrics tests API, it will create API calls for each FairTest defined
    in the `metrics` folder.

    ```python title="main.py"
    from fair_test import FairTestAPI

    app = FairTestAPI(
        title='FAIR enough metrics tests API',
        metrics_folder_path='metrics',

        description="FAIR Metrics tests API for resources related to research. Follows the specifications described by the [FAIRMetrics](https://github.com/FAIRMetrics/Metrics) working group.",
        license_info = {
            "name": "MIT license",
            "url": "https://opensource.org/licenses/MIT"
        },
    )
    ```
    """

    def __init__(
        self,
        *args,
        title: str = "FAIR Metrics Test API",
        description="FAIR Metrics Test API for online resources. Follows the specifications described by the [FAIRMetrics](https://github.com/FAIRMetrics/Metrics) working group. \nBuilt with the [**fair-test** library](https://maastrichtu-ids.github.io/fair-test)",
        version="0.1.0",
        cors_enabled=True,
        public_url="https://metrics.api.fair-enough.semanticscience.org",
        metrics_folder_path="metrics",
        contact={
            "name": settings.CONTACT_NAME,
            "email": settings.CONTACT_EMAIL,
            "url": settings.CONTACT_URL,
            "x-id": settings.CONTACT_ORCID,
        },
        license_info={
            "name": "MIT license",
            "url": "https://opensource.org/licenses/MIT",
        },
        **kwargs,
    ) -> None:
        self.title = title
        self.description = description
        self.version = version
        self.public_url = public_url
        self.metrics_folder_path = metrics_folder_path

        # Instantiate FastAPI
        super().__init__(
            title=title,
            description=description,
            version=version,
            contact=contact,
            license_info=license_info,
        )

        if cors_enabled:
            self.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        metrics_module = metrics_folder_path.replace("/", ".")

        # First get the metrics tests filepath
        assess_name_list = self.get_metrics_tests_filepaths()

        # Then import each metric test listed in the metrics folder
        for assess_name in assess_name_list:
            assess_module = assess_name.replace("/", ".")
            import importlib

            metric_test = importlib.import_module(f"{metrics_module}.{assess_module}").MetricTest
            metric = metric_test()

            try:
                # cf. https://github.com/tiangolo/fastapi/blob/master/fastapi/routing.py#L479
                self.add_api_route(
                    path=f"/tests/{metric.metric_path}",
                    methods=["POST"],
                    endpoint=metric.do_evaluate,
                    name=metric.title,
                    openapi_extra={"description": metric.description},
                    tags=[metric.applies_to_principle],
                )

                self.add_api_route(
                    path=f"/tests/{metric.metric_path}",
                    methods=["GET"],
                    endpoint=metric.openapi_yaml,
                    name=metric.title,
                    openapi_extra={"description": metric.description},
                    tags=[metric.applies_to_principle],
                )
            except Exception:
                print("❌ No API defined for " + metric.metric_path)

        @self.get("/", include_in_schema=False)
        def redirect_root_to_docs():
            # Redirect the route / to /docs
            return RedirectResponse(url="/docs")

    def get_metrics_tests_filepaths(self):
        assess_name_list = []
        for path, _subdirs, files in os.walk(self.metrics_folder_path):
            for filename in files:
                if not path.endswith("__pycache__") and not filename.endswith("__init__.py"):
                    filepath = path.replace(self.metrics_folder_path, "")
                    if filepath:
                        assess_name_list.append(filepath[1:] + "/" + filename[:-3])
                    else:
                        assess_name_list.append(filename[:-3])
        return assess_name_list

    def get_metrics_tests_tests(self):
        metrics_module = self.metrics_folder_path.replace("/", ".")
        metrics_paths = self.get_metrics_tests_filepaths()
        test_tests = []
        for metrics_name in metrics_paths:
            assess_module = metrics_name.replace("/", ".")
            import importlib

            metric_test = importlib.import_module(f"{metrics_module}.{assess_module}").MetricTest

            metric = metric_test()
            for subj, score in metric.test_test.items():
                test_tests.append({"subject": subj, "score": score, "metric_id": metric.metric_path})
        return test_tests

    def run_tests(self, test_endpoint, metric: str = None):
        """
        Run `pytest` tests for each metric test. URLs to test and expected scores are defined with the `test_test` attribute.
        Use this in a test file to automatically test all metrics tests, for example:

        ```python title='tests/test_metrics.py'
        from fastapi.testclient import TestClient
        from fair_test import FairTestAPI

        app = FairTestAPI(metrics_folder_path='metrics')
        endpoint = TestClient(app)

        def test_api():
            app.run_tests(endpoint)
        ```

        Parameters:
            test_endpoint (TestClient): FastAPI TestClient of the app to test
        """
        eval_list = self.get_metrics_tests_tests()
        red = "\033[91m"
        bold = "\033[1m"
        end = "\033[0m"
        yellow = "\033[33m"
        cyan = "\033[36m"

        run_evals = [ev for ev in eval_list if ev["metric_id"] == metric] if metric else eval_list

        print(f"⏳️ Running tests for {bold}{len(run_evals)}{end} metric/subject/score combinations")

        # Test POST metrics evaluation request
        for evl in run_evals:
            if metric and metric != evl["metric_id"]:
                continue
            print(
                f"Testing {yellow}{evl['subject']}{end} with {cyan}{evl['metric_id']}{end} (expect {bold + str(evl['score']) + end})"
            )
            r = test_endpoint.post(
                f"/tests/{evl['metric_id']}",
                json={"subject": evl["subject"]},
                headers={"Accept": "application/json"},
            )
            assert r.status_code == 200
            res = r.json()
            # Check score:
            score = int(res[0]["http://semanticscience.org/resource/SIO_000300"][0]["@value"])
            if score != evl["score"]:
                print(
                    f"❌ Wrong score: got {red}{score}{end} instead of {red}{evl['score']}{end} for {bold}{evl['subject']}{end} with the metric test {bold}{evl['metric_id']}{end}"
                )
            assert score == evl["score"]

        # Test get YAML
        metrics_id_to_test = set()
        for evl in eval_list:
            metrics_id_to_test.add(evl["metric_id"])
        for metric_id in list(metrics_id_to_test):
            r = test_endpoint.get(f"/tests/{metric_id}")
            assert r.status_code == 200
            api_yaml = yaml.safe_load(r.text)
            assert api_yaml["info"]["title"]
            assert api_yaml["info"]["x-applies_to_principle"]
            assert api_yaml["info"]["x-tests_metric"]

        # test bad request
        for metric_id in list(metrics_id_to_test):
            response = test_endpoint.post(
                f"/tests/{metric_id}",
                json={"subject": ""},
                headers={"accept": "application/json"},
            )
            assert response.status_code == 422
            break

        # test 404
        response = test_endpoint.get("/dont-exist", headers={"accept": "application/json"})
        assert response.status_code == 404

        # test redirect
        response = test_endpoint.get("/")
        assert response.status_code == 200

        print(
            f"✅ Successfully tested a total of {bold}{len(run_evals)}{end} FAIR metrics tests/subjects/score combinations"
        )
