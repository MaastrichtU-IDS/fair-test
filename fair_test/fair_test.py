from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Optional, List
import datetime
import urllib.parse
import json
import requests
from rdflib import ConjunctiveGraph
import html
import yaml
import extruct
from fair_test.config import settings
from pyld import jsonld
# pyld required to parse jsonld with rdflib


class TestInput(BaseModel):
    subject: str = settings.DEFAULT_SUBJECT


class FairTest(BaseModel):
    subject: Optional[str]
    comment: List = []
    score: int = 0
    score_bonus: int = 0
    date: str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+01:00")
    metric_version: str  = '0.1.0'
    metric_path: str
    applies_to_principle: str
    id: Optional[str] # URL of the test results
    title: str
    description: str
    author: str = settings.CONTACT_ORCID
    data: Optional[dict]
    default_subject: str = settings.DEFAULT_SUBJECT
    

    def __init__(self) -> None:
        super().__init__()
        self.id = f"{settings.HOST_URL}/metrics/{self.metric_path}#{urllib.parse.quote(str(self.subject))}/result-{self.date}"
        self.data = {
            'alternative_uris': [self.subject]
        }


    class Config:
        arbitrary_types_allowed = True


    def response(self) -> list:
        return JSONResponse(self.toJsonld())


    def toJsonld(self) -> list:
        # To see the object used by the original FAIR metrics:
        # curl -L -X 'POST' -d '{"subject": ""}' 'https://w3id.org/FAIR_Tests/tests/gen2_unique_identifier'
        return [
            {
                "@id": self.id,
                "@type": [
                    "http://fairmetrics.org/resources/metric_evaluation_result"
                ],
                "http://purl.obolibrary.org/obo/date": [
                    {
                        "@value": self.date,
                        "@type": "http://www.w3.org/2001/XMLSchema#date"
                    }
                ],
                "http://schema.org/softwareVersion": [
                {
                    "@value": self.metric_version,
                    "@type": "http://www.w3.org/2001/XMLSchema#float"
                }
                ],
                "http://schema.org/comment": [
                    {
                    "@value": '\n\n'.join(self.comment),
                    "@language": "en"
                    }
                ],
                "http://semanticscience.org/resource/SIO_000332": [
                    {
                    "@value": str(self.subject),
                    "@language": "en"
                    }
                ],
                "http://semanticscience.org/resource/SIO_000300": [
                    {
                    "@value": float(self.score),
                    "@type": "http://www.w3.org/2001/XMLSchema#float"
                    }
                ]
            }
        ]

    # Logging utilities
    def log(self, log_msg: str, prefix: str = None):
        # Add timestamp?
        # log_msg = '[' + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")) + '] ' + log_msg 
        if prefix:
            log_msg = prefix + ' ' + log_msg
        self.comment.append(log_msg)
        print(log_msg)

    def warn(self, log_msg: str):
        self.log(log_msg, 'WARN:')
    
    def info(self, log_msg: str):
        self.log(log_msg, 'INFO:')

    def failure(self, log_msg: str):
        self.score = 0
        self.log(log_msg, 'FAILURE:')

    def success(self, log_msg: str):
        if self.score >= 1:
            self.bonus(log_msg)
        else:
            self.score += 1
            self.log(log_msg, 'SUCCESS:')

    def bonus(self, log_msg: str):
        self.score_bonus += 1
        self.log(log_msg, 'SUCCESS:')


    # Get RDF from an URL (returns RDFLib Graph)
    # Use signposting links to find links to download metadata from (rel=alternate)
    # https://datatracker.ietf.org/doc/html/draft-nottingham-http-link-header-10#section-6.2.2
    def getRDF(self, 
            url: str, 
            use_harvester: bool = False, 
            harvester_url: str = 'https://fair-tests.137.120.31.101.nip.io/tests/harvester',
    ):
        if use_harvester == True:
            # Check the harvester response:
            # curl -X POST -d '{"subject": "https://doi.org/10.1594/PANGAEA.908011"}' https://fair-tests.137.120.31.101.nip.io/tests/harvester
            res = requests.post(harvester_url,
                json={"subject": url},
                # headers={"Accept": "application/ld+json"}
            )
            print(res.text)
            return self.parseRDF(res.text, 'text/turtle', msg='FAIR evaluator harvester RDF')

        self.info(f'Checking if Signposting links can be found in the resource URI headers at {url}')
        # https://github.com/FAIRMetrics/Metrics/blob/master/MetricsEvaluatorCode/Ruby/metrictests/fair_metrics_utilities.rb#L355
        found_signposting = False
        # Check if URL resolve and if redirection
        r = requests.head(url)
        r = requests.get(url)
        r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
        self.info(f'Successfully resolved {url}')
        if r.history:
            self.info(f"Request was redirected to {r.url}. Adding as alternative URI")
            self.data['alternative_uris'].append(r.url)
        if 'link' in r.headers.keys():
            signposting_links = r.headers['link']
            found_signposting = True
        if 'Link' in r.headers.keys():
            signposting_links = r.headers['Link']
            found_signposting = True
        if found_signposting:
            self.info(f'Found Signposting links: {str(signposting_links)}')
            # self.data['signposting'] = str(signposting_links)
            # TODO: parse signposting links, get alternate and meta?
            # return self.getRDF(str(signposting_links))
        else:
            self.warn('Could not find Signposting links')

        # We need to do direct content negociation to turtle and json
        # because some URLs dont support standard weighted content negociation
        check_mime_types = [ 'text/turtle', 'application/ld+json', 'text/turtle, application/turtle, application/x-turtle;q=0.9, application/ld+json;q=0.8, application/rdf+xml, text/n3, text/rdf+n3;q=0.7' ]
        html_text = None
        for mime_type in check_mime_types:
            try:
                r = requests.get(url, headers={'accept': mime_type})
                r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
                contentType = r.headers['Content-Type'].replace(' ', '').replace(';charset=utf-8', '')
                # If return text/plain we parse as turtle
                contentType = contentType.replace('text/plain', 'text/turtle')
                self.info(f'Found some metadata in {contentType} when asking for {mime_type}')
                if contentType.startswith('text/html'):
                    # If HTML we check later with extruct
                    html_text = r.text
                    continue
                try:
                    # If return JSON-LD
                    self.data['json-ld'] = r.json()
                    return self.parseRDF(r.json(), contentType, msg='content negotiation RDF')
                except Exception:
                    # If returns RDF, such as turtle
                    return self.parseRDF(r.text, contentType, msg='content negotiation RDF')
            except Exception:
                self.warn(f'Could not find metadata with content-negotiation when asking for: {mime_type}')
                # Error: e.args[0]

        self.log('INFO: Checking for metadata embedded in the HTML page returned by the resource URI ' + url + ' using extruct')
        try:
            if not html_text:
                get_uri = requests.get(url, headers={'Accept': 'text/html'})
                html_text = html.unescape(get_uri.text)
            try:
                extructed = extruct.extract(html_text.encode('utf8'))
                self.data['extruct'] = extructed
                self.log(f"INFO: found metadata with extruct in the formats: {', '.join(extructed.keys())}")
                if extructed['json-ld']:
                    return self.parseRDF(extructed['json-ld'], 'json-ld', msg='HTML embedded RDF')
                # Check extruct results:
                # for format in extructed.keys():
                #     if extructed[format]:
                #         if format == 'dublincore' and extructed[format] == [{"namespaces": {}, "elements": [], "terms": []}]:
                #             # Handle case where extruct generate empty dict
                #             continue
                #         eval.data['extruct'][format] = extructed[format]
            except Exception as e:
                self.warn('Error when parsing the subject URL HTML embedded JSON-LD from ' + url + ' using extruct. Getting: ' + str(e.args[0]))

        except Exception as e:
            self.warn('Error when running extruct on ' + url + '. Getting: ' + str(e.args[0]))

        return ConjunctiveGraph()


    def parseRDF(self, rdf_data, mime_type: str = None, msg: str = ''):
        # https://rdflib.readthedocs.io/en/stable/plugin_parsers.html
        # rdflib_formats = ['turtle', 'json-ld', 'xml', 'ntriples', 'nquads', 'trig', 'n3']
        # We need to make this ugly fix because regular content negotiation dont work with schema.org
        # https://github.com/schemaorg/schemaorg/issues/2578
        if type(rdf_data) == dict:
            rdf_data = [rdf_data]
        if type(rdf_data) == list:
            for rdf_entry in rdf_data:
                if '@context' in rdf_entry and (rdf_entry['@context'].startswith('http://schema.org') or rdf_entry['@context'].startswith('https://schema.org')):
                    rdf_entry['@context'] = 'https://schema.org/docs/jsonldcontext.json'
            # RDFLib JSON-LD has issue with encoding: https://github.com/RDFLib/rdflib/issues/1416
            rdf_data = jsonld.expand(rdf_data)
            rdf_data = json.dumps(rdf_data)
            mime_type = 'json-ld'
        
        g = ConjunctiveGraph()
        try:
            g.parse(data=rdf_data, format=mime_type)
            self.info(f'{str(len(g))} triples parsed. Metadata from {mime_type} {msg} parsed with RDFLib parser {mime_type}')
        except Exception as e:
            self.warn('Could not parse ' + mime_type + ' metadata from ' + msg + ' with RDFLib parser ' + mime_type + ' ' + str(e))

        return g


    def doEvaluate(self, input: TestInput):
        if input.subject == '':
            raise HTTPException(status_code=422, detail=f"Provide a subject URL to evaluate")
        self.subject = input.subject
        return self.evaluate()


    # Function used for the GET YAML call for each Metric Test
    def evaluate(self):
        return JSONResponse({
            'errorMessage': 'Not implemented'
        })


    # https://github.com/LUMC-BioSemantics/RD-FAIRmetrics/blob/main/docs/yaml/RD-R1.yml
    # Function used for the GET YAML call for infos about each Metric Test
    def openapi_yaml(self):
        metric_info = {
          "swagger": "2.0",
          "info": {
            "version": f"{str(self.metric_version)}",
            "title": self.title,
            "x-tests_metric": f"{settings.HOST_URL}/tests/{self.metric_path}",
            "description": self.description,
            "x-applies_to_principle": self.applies_to_principle,
            "contact": {
              "x-organization": settings.ORG_NAME,
              "url": settings.CONTACT_URL,
              "name": settings.CONTACT_NAME,
              "x-role": "responsible developer",
              "email": settings.CONTACT_EMAIL,
              "x-id": self.author,
            }
          },
          "host": settings.HOST,
          "basePath": "/tests/",
          "schemes": [
            "https"
          ],
          "paths": {
            self.metric_path: {
              "post": {
                "parameters": [
                  {
                    "name": "content",
                    "in": "body",
                    "required": True,
                    "schema": {
                      "$ref": "#/definitions/schemas"
                    }
                  }
                ],
                "consumes": [
                  "application/json"
                ],
                "produces": [
                  "application/json"
                ],
                "responses": {
                  "200": {
                    "description": "The response is a binary (1/0), success or failure"
                  }
                }
              }
            }
          },
          "definitions": {
            "schemas": {
              "required": [
                "subject"
              ],
              "properties": {
                "subject": {
                  "type": "string",
                  "description": "the GUID being tested"
                }
              }
            }
          }
        }
        api_yaml = yaml.dump(metric_info, indent=2)
        return PlainTextResponse(content=api_yaml, media_type='text/x-yaml')

