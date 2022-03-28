from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Optional, List, Any
import datetime
import urllib.parse
import json
import requests
from rdflib import ConjunctiveGraph, URIRef, RDF
from rdflib.namespace import FOAF
import html
import yaml
import extruct
from fair_test.config import settings
from pyld import jsonld
# pyld is required to parse jsonld with rdflib


# class MetricInput(BaseModel):
#     subject: str = settings.DEFAULT_SUBJECT


class FairTestEvaluation(BaseModel):
    """
    Class to manipulate a FAIR metrics test evaluation. Provides helpers functions to easily retrieve and parse metadata.
    A new FairTestEvaluation object is create for each new request to one of the FAIR metrics test API call exposed by the API

    ```python title="metrics/a1_check_something.py"
    from fair_test import FairTest
    
    class MetricTest(FairTest):
        metric_path = 'a1-check-something'
        applies_to_principle = 'A1'
        title = 'Check something'
        description = "Test something"
        author = 'https://orcid.org/0000-0000-0000-0000'
        metric_version = '0.1.0'

        def evaluate(self):
            self.info(f'Checking something for {self.subject}')
            g = self.retrieve_rdf(self.subject, use_harvester=False)
            if len(g) > 0:
                self.success(f'{len(g)} triples found, test sucessful')
            else:
                self.failure('No triples found, test failed')
            return self.response()
    ```
    """
    subject: Optional[str]
    score: int = 0
    score_bonus: int = 0
    comment: List = []
    date: str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+01:00")
    metric_version: str  = '0.1.0'
    id: Optional[str] # URL of the test results
    data: Optional[dict] = {}

    def __init__(self, subject: str, metric_path: str) -> None:
        super().__init__()
        self.subject = subject
        self.id = f"{settings.HOST_URL}/metrics/{metric_path}#{urllib.parse.quote(str(self.subject))}/result-{self.date}"
        # self.comment = []
        # self.data = {}

        alt_uris = set()
        alt_uris.add(self.subject)
        # Add HTTPS/HTTPS counterpart as alternative URIs
        if self.subject.startswith('http://'):
            alt_uris.add(self.subject.replace('http://', 'https://'))
        elif self.subject.startswith('https://'):
            alt_uris.add(self.subject.replace('https://', 'http://'))
        
        # Fix to add an alternative URI for doi.org that is commonly used as identifier in the metadata
        if self.subject.startswith('https://doi.org/'):
            alt_uris.add(self.subject.replace('https://doi.org/', 'http://dx.doi.org/'))
            alt_uris.add(self.subject.lower())
        if self.subject.startswith('http://doi.org/'):
            alt_uris.add(self.subject.replace('http://doi.org/', 'http://dx.doi.org/'))
            alt_uris.add(self.subject.lower())

        self.data['alternative_uris'] = list(alt_uris)


    class Config:
        arbitrary_types_allowed = True



    # TODO: Use signposting links to find links to download metadata from (rel=alternate)
    # https://datatracker.ietf.org/doc/html/draft-nottingham-http-link-header-10#section-6.2.2
    # TODO: implement metadata extraction with more tools? 
    # e.g. Apache Tika for PDF/pptx? or ruby Kellog's Distiller? http://rdf.greggkellogg.net/distiller
    # c.f. https://github.com/FAIRMetrics/Metrics/blob/master/MetricsEvaluatorCode/Ruby/metrictests/fair_metrics_utilities.rb
    def retrieve_rdf(self, 
            url: str, 
            use_harvester: bool = False, 
            harvester_url: str = 'https://fair-tests.137.120.31.101.nip.io/tests/harvester',
    ):
        """
        Retrieve RDF from an URL.

        Parameters:
            url (str): URL to retrieve RDF from
            use_harvester (bool, optional): Use an external harvester to retrieve the RDF instead of the built-in python harvester 
            harvester_url (str, optional): URL of the RDF harvester used

        Returns:
            g (Graph): A RDFLib Graph with the RDF found at the given URL
        """
        if use_harvester == True:
            # Check the harvester response:
            # curl -X POST -d '{"subject": "https://doi.org/10.1594/PANGAEA.908011"}' https://fair-tests.137.120.31.101.nip.io/tests/harvester
            try:
                self.info(f'Using Harvester at {harvester_url} to retrieve RDF metadata at {url}')
                res = requests.post(harvester_url,
                    json={"subject": url},
                    timeout=60,
                    # headers={"Accept": "application/ld+json"}
                )
                return self.parse_rdf(res.text, 'text/turtle', log_msg='FAIR evaluator harvester RDF')
            except Exception as e:
                self.warn(f'Failed to reach the Harvester at {harvester_url}, using the built-in python harvester')

        self.info(f'Checking if Signposting links can be found in the resource URI headers at {url}')
        # https://github.com/FAIRMetrics/Metrics/blob/master/MetricsEvaluatorCode/Ruby/metrictests/fair_metrics_utilities.rb#L355
        found_signposting = False
        # Check if URL resolve and if redirection
        # r = requests.head(url)
        r = requests.get(url)
        r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
        self.info(f'Successfully resolved {url}')
        if r.history:
            self.info(f"Request was redirected to {r.url}. Adding as alternative URI: {', '.join(self.data['alternative_uris'])}")
            self.data['alternative_uris'].append(r.url)
        if 'link' in r.headers.keys():
            signposting_links = r.headers['link']
            found_signposting = True
        if 'Link' in r.headers.keys():
            signposting_links = r.headers['Link']
            found_signposting = True
        if found_signposting:
            self.info(f'Found Signposting links: {str(signposting_links)}')
            self.data['signposting'] = str(signposting_links)
            # TODO: parse signposting links, get alternate and meta?
            # return self.retrieve_rdf(str(signposting_links))
        else:
            self.info('Could not find Signposting links')

        # We need to do direct content negociation to turtle and json
        # because some URLs dont support standard weighted content negociation
        check_mime_types = [ 'text/turtle', 'application/ld+json', 'text/turtle, application/turtle, application/x-turtle;q=0.9, application/ld+json;q=0.8, application/rdf+xml, text/n3, text/rdf+n3;q=0.7' ]
        html_text = None
        for mime_type in check_mime_types:
            try:
                r = requests.get(url, headers={'accept': mime_type})
                r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
                content_type = r.headers['Content-Type'].replace(' ', '').replace(';charset=utf-8', '')
                # If return text/plain we parse as turtle
                content_type = content_type.replace('text/plain', 'text/turtle')
                self.info(f'Found some metadata in {content_type} when asking for {mime_type}')
                if content_type.startswith('text/html'):
                    # If HTML we check later with extruct
                    html_text = r.text
                    continue
                try:
                    # If return JSON-LD
                    self.data['json-ld'] = r.json()
                    return self.parse_rdf(r.json(), content_type, log_msg='content negotiation RDF')
                except Exception:
                    # If returns RDF, such as turtle
                    return self.parse_rdf(r.text, content_type, log_msg='content negotiation RDF')
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
                    return self.parse_rdf(extructed['json-ld'], 'json-ld', log_msg='HTML embedded RDF')
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


    def parse_rdf(self, rdf_data, mime_type: str = None, log_msg: str = ''):
        """
        Parse any string or JSON-like object to a RDFLib Graph

        Parameters:
            rdf_data (str|object): Text or object to convert to RDF
            mime_type (str, optional): Mime type of the data to convert
            log_msg (str, optional): Text to use when logging about the parsing process (help debugging)

        Returns:
            g (Graph): A RDFLib Graph
        """
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
            self.info(f'{str(len(g))} triples parsed. Metadata from {mime_type} {log_msg} parsed with RDFLib parser {mime_type}')
        except Exception as e:
            self.warn('Could not parse ' + mime_type + ' metadata from ' + log_msg + ' with RDFLib parser ' + mime_type + ' ' + str(e))

        return g


    def extract_prop(self, g, preds, subj = None):
        """
        Helper to extract properties from a RDFLib Graph

        Parameters:
            g (Graph): RDFLib Graph
            pred (list): Lit of predicates to find value for
            subj (list, optional): Optionally also limit the results for a list of subjects

        Returns:
            props (list): A list of the values found for the given properties
        """
        values = set()
        check_preds = set()
        for pred in preds:
            check_preds.add(URIRef(str(pred)))
            # Add the http/https counterpart for each predicate
            if str(pred).startswith('http://'):
                check_preds.add(URIRef(str(pred).replace('http://', 'https://')))
            elif str(pred).startswith('https://'):
                check_preds.add(URIRef(str(pred).replace('https://', 'http://')))

        self.info(f"Checking values for properties: {preds}")
        if subj:
            self.info(f"Checking values for subjects URIs: {str(subj)}")

        for pred in list(check_preds):
            if isinstance(subj, list):
                test_subjs = [URIRef(str(s)) for s in subj] 
            elif subj:
                test_subjs = [URIRef(str(subj))]
            else:
                test_subjs = [None]
            for test_subj in test_subjs:
                for s, p, o in g.triples((test_subj, pred, None)):
                    self.info(f"Found a value for property {str(pred)} => {str(o)}")
                    values.add(str(o))

        return list(values)


    def extract_data_uri(self, g):
        """
        Helper to easily retrieve the URI of the data from RDF metadata (RDFLib Graph)

        Parameters:
            g (Graph): RDFLib Graph

        Returns:
            data_uri (list): List of URI found for the data in the metadata
        """
        data_props = [
            "https://www.w3.org/ns/ldp#contains", 
            "https://xmlns.com/foaf/0.1/primaryTopic", 
            "https://schema.org/about", 
            "https://schema.org/mainEntity", 
            "https://schema.org/codeRepository",
            "https://schema.org/distribution", 
            "https://www.w3.org/ns/dcat#distribution", 
            "https://semanticscience.org/resource/SIO_000332", 
            "https://semanticscience.org/resource/is-about", 
            "https://purl.obolibrary.org/obo/IAO_0000136"
        ]
        http_props = [p.replace('https://', 'http://') for p in data_props] 
        self.info(f"Searching for the data URI using the following predicates: {', '.join(data_props + http_props)}")
        return self.extract_prop(g, preds=data_props + http_props, subj=self.data['alternative_uris'])



    def response(self) -> list:
        """
        Function used to generate the FAIR metric test results as JSON-LD, and return this JSON-LD as HTTP response

        Returns:
            response (JSONResponse): HTTP response containing the test results as JSON-LD
        """
        return JSONResponse(self.to_jsonld())


    def to_jsonld(self) -> list:
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
                ],
                "http://semanticscience.org/resource/metadata": self.data
            }
        ]

    # Logging utilities
    def log(self, log_msg: str, prefix: str = None):
        # Add timestamp?
        # log_msg = '[' + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")) + '] ' + log_msg 
        if prefix:
            log_msg = prefix + ' ' + log_msg
        self.comment.append(log_msg)
        # print(log_msg)

    def warn(self, log_msg: str):
        """
        Log a warning related to the FAIR test execution (add to the comments of the test)

        Parameters:
            log_msg (str): Message to log
        """
        self.log(log_msg, 'WARN:')
    
    def info(self, log_msg: str):
        """
        Log an info message related to the FAIR test execution (add to the comments of the test)

        Parameters:
            log_msg (str): Message to log
        """
        self.log(log_msg, 'INFO:')

    def failure(self, log_msg: str):
        """
        Log a failure message related to the FAIR test execution (add to the comments of the test and set score to 0)

        Parameters:
            log_msg (str): Message to log
        """
        self.score = 0
        self.log(log_msg, 'FAILURE:')

    def success(self, log_msg: str):
        """
        Log a success message related to the FAIR test execution (add to the comments of the test and set score to 1)

        Parameters:
            log_msg (str): Message to log
        """
        if self.score >= 1:
            self.bonus(log_msg)
        else:
            self.score += 1
            self.log(log_msg, 'SUCCESS:')

    def bonus(self, log_msg: str):
        self.score_bonus += 1
        self.log(log_msg, 'SUCCESS:')


