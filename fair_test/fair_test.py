from typing import Optional

import yaml
from fastapi import HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel

from fair_test import FairTestEvaluation
from fair_test.config import settings


class MetricInput(BaseModel):
    subject: str = settings.DEFAULT_SUBJECT


class FairTest(BaseModel):
    """
    Class to define a FAIR metrics test,
    API calls will be automatically generated for this test when the FairTestAPI is started.

    ```python title="metrics/a1_check_something.py"
    from fair_test import FairTest, FairTestEvaluation

    class MetricTest(FairTest):
        metric_path = 'a1-check-something'
        applies_to_principle = 'A1'
        title = 'Check something'
        description = "Test something"
        author = 'https://orcid.org/0000-0000-0000-0000'
        metric_version = '0.1.0'
        test_test={
            'http://doi.org/10.1594/PANGAEA.908011': 1,
            'https://github.com/MaastrichtU-IDS/fair-test': 0,
        }

        def evaluate(self, eval: FairTestEvaluation):
            eval.info(f'Checking something for {self.subject}')
            g = eval.retrieve_metadata(self.subject, use_harvester=False)
            if len(g) > 0:
                eval.success(f'{len(g)} triples found, test sucessful')
            else:
                eval.failure('No triples found, test failed')
            return eval.response()
    ```
    """

    # subject: Optional[str]
    # comment: List = []
    # score: int = 0
    # score_bonus: int = 0
    # date: str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+01:00")
    metric_version: str = "0.1.0"
    metric_path: str
    applies_to_principle: str
    id: Optional[str]  # URL of the test results
    title: str
    description: str
    metric_readme_url: Optional[str]

    default_subject: str = settings.DEFAULT_SUBJECT
    topics = []
    test_test = {}
    # topics: List[str] = []
    # test_test: Dict[str, int] = {}

    author: str = settings.CONTACT_ORCID
    contact_url: str = settings.CONTACT_URL
    contact_name: str = settings.CONTACT_NAME
    contact_email: str = settings.CONTACT_EMAIL
    organization: str = settings.ORG_NAME
    # metric_readme_url: str = None

    def __init__(self) -> None:
        super().__init__()

        if not self.metric_readme_url:
            self.metric_readme_url = f"{settings.HOST_URL}/tests/{self.metric_path}"

    class Config:
        arbitrary_types_allowed = True

    def do_evaluate(self, input: MetricInput):
        if input.subject == "":
            raise HTTPException(status_code=422, detail=f"Provide a subject URL to evaluate")

        # TODO: create separate object for each FAIR test evaluation to avoid any conflict? e.g. FairTestEvaluation
        eval = FairTestEvaluation(input.subject, self.metric_path)
        # self.subject = input.subject

        return self.evaluate(eval)
        # try:
        #     return self.evaluate(eval)
        # except Exception e:
        #     return JSONResponse({
        #         'errorMessage': f'Error while running the evaluation against {input.subject}'
        #     })

    # Placeholder that will be overwritten for each Metric Test
    def evaluate(self, eval: FairTestEvaluation):
        return JSONResponse({"errorMessage": "Not implemented"})

    # https://github.com/LUMC-BioSemantics/RD-FAIRmetrics/blob/main/docs/yaml/RD-R1.yml
    # Function used for the GET YAML call for infos about each Metric Test
    def openapi_yaml(self):
        metric_info = {
            "swagger": "2.0",
            "info": {
                "version": f"{str(self.metric_version)}",
                "title": self.title,
                "x-tests_metric": self.metric_readme_url,
                "description": self.description,
                "x-applies_to_principle": self.applies_to_principle,
                "x-topics": self.topics,
                "contact": {
                    "x-organization": self.organization,
                    "url": self.contact_url,
                    # "name": self.contact_name.encode('latin1').decode('iso-8859-1'),
                    "name": self.contact_name,
                    "x-role": "responsible developer",
                    "email": self.contact_email,
                    "x-id": self.author,
                },
            },
            "host": settings.HOST_URL.replace("https://", "").replace("http://", ""),
            "basePath": "/tests/",
            "schemes": ["https"],
            "paths": {
                self.metric_path: {
                    "post": {
                        "parameters": [
                            {
                                "name": "content",
                                "in": "body",
                                "required": True,
                                "schema": {"$ref": "#/definitions/schemas"},
                            }
                        ],
                        "consumes": ["application/json"],
                        "produces": ["application/json"],
                        "responses": {"200": {"description": "The response is a binary (1/0), success or failure"}},
                    }
                }
            },
            "definitions": {
                "schemas": {
                    "required": ["subject"],
                    "properties": {
                        "subject": {
                            "type": "string",
                            "description": "the GUID being tested",
                        }
                    },
                }
            },
        }
        api_yaml = yaml.dump(metric_info, indent=2, allow_unicode=True)
        return PlainTextResponse(content=api_yaml, media_type="text/x-yaml")
