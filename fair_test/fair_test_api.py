from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse 
from typing import Optional
from fastapi import APIRouter
import os
import importlib
import pathlib

import pkg_resources
import logging
import re
from urllib import parse
# import os


class FairTestAPI(FastAPI):
    """
    Class to deploy a SPARQL endpoint using a RDFLib Graph
    """

    def __init__(self,
            *args,
            title: str = "SPARQL endpoint for RDFLib graph", 
            description="A SPARQL endpoint to serve machine learning models, or any other logic implemented in Python. \n[Source code](https://github.com/MaastrichtU-IDS/fair-test)",
            version="0.1.0",
            cors_enabled=True,
            public_url='https://metrics.api.fair-enough.semanticscience.org/sparql',
            metrics_folder_path='metrics', 
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
        )

        if cors_enabled:
            self.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        api_responses={
            200: {
                "description": "SPARQL query results",
                "content": {
                    "application/sparql-results+json": {
                        "results": {"bindings": []}, 'head': {'vars': []}
                    },
                    "application/json": {
                        "results": {"bindings": []}, 'head': {'vars': []}
                    },
                    "text/csv": {
                        "example": "s,p,o"
                    },
                    "application/sparql-results+csv": {
                        "example": "s,p,o"
                    },
                    "text/turtle": {
                        "example": "service description"
                    },
                    "application/sparql-results+xml": {
                        "example": "<root></root>"
                    },
                    "application/xml": {
                        "example": "<root></root>"
                    },
                    # "application/rdf+xml": {
                    #     "example": '<?xml version="1.0" encoding="UTF-8"?> <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"></rdf:RDF>'
                    # },
                },
            },
            400:{
                "description": "Bad Request",
            },
            403:{
                "description": "Forbidden",
            }, 
            422:{
                "description": "Unprocessable Entity",
            },
        }

        mimetype={
            'turtle': 'text/turtle',
            'xml_results': 'application/sparql-results+xml'
        }

        # metrics_folder = metrics_folder_path.split('/')[-1]
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

        assess_list = []
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
            except Exception as e:
                print('❌ No API defined for ' + metric.metric_path)

        @self.get("/", include_in_schema=False)
        def redirect_root_to_docs():
            """Redirect the route / to /docs"""
            return RedirectResponse(url='/docs')
