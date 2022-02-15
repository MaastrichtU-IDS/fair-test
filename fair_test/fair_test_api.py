from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
# from starlette.responses import FileResponse 
import os
from fair_test.config import settings


class FairTestAPI(FastAPI):
    """
    Class to deploy a SPARQL endpoint using a RDFLib Graph
    """

    def __init__(self,
            *args,
            title: str = "SPARQL endpoint for RDFLib graph", 
            description="FAIR Metrics tests API for online resources. Follows the specifications described by the [FAIRMetrics](https://github.com/FAIRMetrics/Metrics) working group. \n[Source code](https://github.com/MaastrichtU-IDS/fair-test)",
            version="0.1.0",
            cors_enabled=True,
            public_url='https://metrics.api.fair-enough.semanticscience.org/sparql',
            metrics_folder_path='metrics', 
            contact = {
                "name": settings.CONTACT_NAME,
                "email": settings.CONTACT_EMAIL,
                "url": settings.CONTACT_URL,
                "x-id": settings.CONTACT_ORCID,
            },
            license_info = {
                "name": "MIT license",
                "url": "https://opensource.org/licenses/MIT"
            },
            **kwargs
        ) -> None:
        """
        Constructor of the FAIR testing API, create API calls for each FairTest defined
        in the metrics folder
        """
        self.title=title
        self.description=description
        self.version=version
        self.public_url=public_url
        self.metrics_folder_path=metrics_folder_path

        # Instantiate FastAPI
        super().__init__(
            title=title, description=description, version=version, 
            contact=contact, license_info=license_info,
        )

        if cors_enabled:
            self.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        metrics_module = metrics_folder_path.replace('/', '.')

        # metrics_full_path = f'{str(pathlib.Path(__file__).parent.resolve())}/{metrics_folder_path}'
        metrics_full_path = f'{metrics_folder_path}'

        # First get the metrics tests filepath
        assess_name_list = []
        for path, subdirs, files in os.walk(metrics_full_path):
            for filename in files:
                if not path.endswith('__pycache__') and not filename.endswith('__init__.py'):
                    filepath = path.replace(metrics_full_path, '')
                    if filepath:
                        assess_name_list.append(filepath[1:] + '/' + filename[:-3])
                    else:
                        assess_name_list.append(filename[:-3])

        # Then import each metric test listed in the metrics folder
        for assess_name in assess_name_list:
            assess_module = assess_name.replace('/', '.')
            import importlib
            MetricTest = getattr(importlib.import_module(f'{metrics_module}.{assess_module}'), "MetricTest")

            metric = MetricTest()

            try:
                # cf. https://github.com/tiangolo/fastapi/blob/master/fastapi/routing.py#L479
                self.add_api_route(
                    path=f"/tests/{metric.metric_path}",
                    methods=["POST"],
                    endpoint=metric.doEvaluate,
                    name=metric.title,
                    openapi_extra={
                        'description': metric.description
                    },
                    tags=[metric.applies_to_principle]
                )

                self.add_api_route(
                    path=f"/tests/{metric.metric_path}",
                    methods=["GET"],
                    endpoint=metric.openapi_yaml,
                    name=metric.title,
                    openapi_extra={
                        'description': metric.description
                    },
                    tags=[metric.applies_to_principle]
                )
            except Exception:
                print('❌ No API defined for ' + metric.metric_path)

        @self.get("/", include_in_schema=False)
        def redirect_root_to_docs():
            """Redirect the route / to /docs"""
            return RedirectResponse(url='/docs')
