from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
# from fastapi import HTTPException
# from fastapi.responses import JSONResponse, PlainTextResponse
import datetime
import json
import requests
from urllib.parse import urlparse, quote
from rdflib import ConjunctiveGraph, URIRef, Literal, BNode, RDF
import extruct
from fair_test.config import settings
from pyld import jsonld
# pyld is required to parse jsonld with rdflib


class FairTestEvaluation(BaseModel):
    """
    Class to manipulate a FAIR metrics test evaluation. Provides helpers functions to easily retrieve and parse metadata.
    A new FairTestEvaluation object is create for each new request to one of the FAIR metrics test API call exposed by the API

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
    subject: Optional[str]
    score: int = 0
    score_bonus: int = 0
    comment: List = []
    date: str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+01:00")
    metric_version: str  = '0.1.0'
    id: Optional[str] # URL of the test results
    data: Optional[dict] = {}


    def __init__(self, 
        subject: str, 
        metric_path: str
    ) -> None:
        super().__init__()
        self.subject = subject
        self.id = f"{settings.HOST_URL}/metrics/{metric_path}#{quote(str(self.subject))}/result-{self.date}"

        alt_uris = set()
        alt_uris.add(self.subject)
        # Add HTTPS/HTTPS counterpart as alternative URIs
        if self.subject.startswith('http://'):
            alt_uris.add(self.subject.replace('http://', 'https://'))
        elif self.subject.startswith('https://'):
            alt_uris.add(self.subject.replace('https://', 'http://'))
        
        # Fix to add an alternative URI for doi.org that is commonly used as identifier in the metadata
        parsed_url = urlparse(self.subject)
        if parsed_url.netloc and parsed_url.netloc == 'doi.org':
            alt_uris.add('http://dx.doi.org/' + parsed_url.path[1:])

        self.data['alternative_uris'] = list(alt_uris)


    class Config:
        arbitrary_types_allowed = True


    # TODO: Use signposting to find links to download metadata from (rel=alternate)
    # https://datatracker.ietf.org/doc/html/draft-nottingham-http-link-header-10#section-6.2.2
    # TODO: implement metadata extraction with more tools? 
    # e.g. Apache Tika for PDF/pptx? or ruby Kellog's Distiller? http://rdf.greggkellogg.net/distiller
    # c.f. https://github.com/FAIRMetrics/Metrics/blob/master/MetricsEvaluatorCode/Ruby/metrictests/fair_metrics_utilities.rb
    def retrieve_metadata(self, 
        url: str, 
        use_harvester: Optional[bool] = False, 
        harvester_url: Optional[str] = 'https://fair-tests.137.120.31.101.nip.io/tests/harvester',
    ) -> Any:
        """
        Retrieve metadata from a URL, RDF metadata parsed as a RDFLib Graph in priority. 
        Super useful. It tries:
        - Following signposting links (returned in HTTP headers)  
        - Extracting JSON-LD embedded in the HTML
        - Asking RDF through content-negociation
        - Can return JSON found as a fallback, if RDF metadata is not found
        You can also use an external harvester API to get the RDF metadata

        Parameters:
            url: URL to retrieve RDF from
            use_harvester: Use an external harvester to retrieve the RDF instead of the built-in python harvester 
            harvester_url: URL of the RDF harvester used

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
        html_text = None
        metadata_obj = []
        # Check if URL resolve and if redirection
        # r = requests.head(url)

        try:
            r = requests.get(url)
            r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
            self.info(f'Successfully resolved {url}')
            html_text = r.text
            if r.history:
                # Extract alternative URIs if request redirected
                self.info(f"Request was redirected to {r.url}.")
                redirect_url = r.url
                if redirect_url.startswith('https://linkinghub.elsevier.com/retrieve/pii/'):
                    # Special case to handle Elsevier bad redirections to ScienceDirect
                    redirect_url = redirect_url.replace('https://linkinghub.elsevier.com/retrieve/pii/', 'https://www.sciencedirect.com/science/article/pii/')

                self.data['redirect_url'] = redirect_url
                if url == self.subject and not redirect_url in self.data['alternative_uris']:
                    self.info(f"Adding {redirect_url} to the list of alternative URIs for the subject")
                    self.data['alternative_uris'].append(redirect_url)
                    if r.url.startswith('http://'):
                        self.data['alternative_uris'].append(redirect_url.replace('http://', 'https://'))
                    elif r.url.startswith('https://'):
                        self.data['alternative_uris'].append(redirect_url.replace('https://', 'http://'))

            if 'link' in r.headers.keys():
                signposting_links = r.headers['link']
                found_signposting = True
            if 'Link' in r.headers.keys():
                signposting_links = r.headers['Link']
                found_signposting = True
            if found_signposting:
                self.info(f'Found Signposting links: {str(signposting_links)}')
                self.data['signposting'] = str(signposting_links)
                # TODO: parse signposting links, get alternate and meta? https://signposting.org/FAIR
                # return self.retrieve_metadata(str(signposting_links))
            else:
                self.info('Could not find Signposting links')
        except Exception:
            self.warn(f'Could not resolve the URL: {url}')
            # Error: e.args[0]

        self.info('Checking for metadata embedded in the HTML page returned by the resource URI ' + url + ' using extruct')
        try:
            extructed = extruct.extract(html_text.encode('utf8'))
            if url == self.subject:
                self.data['extruct'] = extructed
            self.info(f"Found metadata with extruct in the formats: {', '.join(extructed.keys())}")
            if len(extructed['json-ld']) > 0:
                g = self.parse_rdf(extructed['json-ld'], 'json-ld', log_msg='HTML embedded JSON-LD RDF')
                if len(g) > 0:
                    return g
                else:
                    metadata_obj = extructed['json-ld']
            if len(extructed['rdfa']) > 0:
                g = self.parse_rdf(extructed['rdfa'], 'json-ld', log_msg='HTML embedded RDFa')
                if len(g) > 0:
                    return g
                elif not metadata_obj:
                    metadata_obj = extructed['rdfa']
            if not metadata_obj and len(extructed['microdata']) > 0:
                metadata_obj = extructed['microdata']
            if not metadata_obj and extructed['dublincore'] != [{"namespaces": {},"elements": [],"terms": []}]:
                # Dublin core always comes as this empty dict if no match 
                metadata_obj = extructed['dublincore']
            # The rest is not extracted because usually give no interesting metadata:
            # opengraph, microformat
        except Exception as e:
            self.info('Error when running extruct on ' + url + '. Getting: ' + str(e.args[0]))


        # Perform content negociation last because it's the slowest for a lot of URLs like zenodo
        # We need to do direct content negociation to turtle and json
        # because some URLs dont support standard weighted content negociation
        check_mime_types = [ 'text/turtle', 'application/ld+json', 'text/turtle, application/turtle, application/x-turtle;q=0.9, application/ld+json;q=0.8, application/rdf+xml, text/n3, text/rdf+n3;q=0.7' ]
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
                    if not metadata_obj:
                        metadata_obj = r.json()
                    return self.parse_rdf(r.json(), content_type, log_msg='content negotiation RDF')
                except Exception:
                    # If returns RDF, such as turtle
                    return self.parse_rdf(r.text, content_type, log_msg='content negotiation RDF')
            except Exception:
                self.info(f'Could not find metadata with content-negotiation when asking for: {mime_type}')
                # Error: e.args[0]

        return metadata_obj


    def parse_rdf(self, 
        rdf_data: Any, 
        mime_type: Optional[str] = None, 
        log_msg: Optional[str] = ''
    ) -> Any:
        """
        Parse any string or JSON-like object to a RDFLib Graph

        Parameters:
            rdf_data (str|object): Text or object to convert to RDF
            mime_type: Mime type of the data to convert
            log_msg: Text to use when logging about the parsing process (help debugging)

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
                try:
                    # Dirty hack to fix RDFLib that is not able to parse JSON-LD schema.org:
                    if '@context' in rdf_entry:
                        if isinstance(rdf_entry['@context'], str):
                            if rdf_entry['@context'].startswith('http://schema.org') or rdf_entry['@context'].startswith('https://schema.org'):
                                rdf_entry['@context'] = 'https://schema.org/docs/jsonldcontext.json'
                        if isinstance(rdf_entry['@context'], list):
                            for i, cont in enumerate(rdf_entry['@context']):
                                if isinstance(cont, str):
                                    rdf_entry['@context'][i] = 'https://schema.org/docs/jsonldcontext.json'
                except:
                    pass
            # RDFLib JSON-LD had issue with encoding: https://github.com/RDFLib/rdflib/issues/1416
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


    def extract_prop(self, 
        g: Any, 
        preds: List[Any], 
        subj: Optional[Any] = None
    ) -> List[Any]:
        """
        Helper to extract properties from a RDFLib Graph

        Parameters:
            g (Graph): RDFLib Graph
            preds: List of predicates to find value for
            subj: Optionally also limit the results for a list of subjects

        Returns:
            props: A list of the values found for the given properties
        """
        values = set()
        check_preds = set()
        for pred in preds:
            # Add the http/https counterpart for each predicate
            check_preds.add(URIRef(str(pred)))
            if str(pred).startswith('http://'):
                check_preds.add(URIRef(str(pred).replace('http://', 'https://')))
            elif str(pred).startswith('https://'):
                check_preds.add(URIRef(str(pred).replace('https://', 'http://')))

        self.info(f"Checking properties values for properties: {preds}")
        if subj:
            self.info(f"Checking properties values for subject URI(s): {str(subj)}")

        for pred in list(check_preds):
            if not isinstance(subj, list):
                subj = [subj]
                # test_subjs = [URIRef(str(s)) for s in subj] 
            for test_subj in subj:
                for s, p, o in g.triples((test_subj, URIRef(str(pred)), None)):
                    self.info(f"Found a value for property {str(pred)} => {str(o)}")
                    values.add(o)

        return list(values)


    def extract_metadata_subject(self, 
        g: Any, 
        alt_uris: Optional[List[str]] = None
    ) -> Any:
        """
        Helper to extract the subject URI to which metadata about the resource is attached in a RDFLib Graph

        Parameters:
            g (Graph): RDFLib Graph
            alt_uris: List of alternative URIs for the subject to find

        Returns:
            subject_uri: The subject URI used as ID in the metadata
        """
        subject_uri = None
        if not alt_uris:
            alt_uris = self.data['alternative_uris']

        preds_id = [
            "https://purl.org/dc/terms/identifier", 
            "https://purl.org/dc/elements/1.1/identifier", 
            "https://schema.org/identifier", 
            "https://schema.org/sameAs",
            "http://ogp.me/ns#url"
        ]
        all_preds_id = [p.replace('https://', 'http://') for p in preds_id] + preds_id
        all_preds_uris = [URIRef(str(s)) for s in all_preds_id] 
        resource_properties = {}
        resource_linked_to = {}

        for alt_uri in alt_uris:
            uri_ref = URIRef(str(alt_uri))
            # Search with the subject URI as triple subject
            for s, p, o in g.triples((uri_ref, None, None)):
                self.info(f"Found subject identifier in metadata: {str(s)}")
                resource_properties[str(p)] = str(o)
                subject_uri = uri_ref

            if not subject_uri:
                # Search with the subject URI as triple object
                for pred in all_preds_uris:
                    for s, p, o in g.triples((None, pred, uri_ref)):
                        self.info(f"Found subject identifier in metadata: {str(s)}")
                        resource_linked_to[str(s)] = str(p)
                        subject_uri = s

                    if not subject_uri:
                        # Also check when URI defined as Literal
                        for s, p, o in g.triples((None, pred, Literal(str(uri_ref)))):
                            self.info(f"Found subject identifier in metadata: {str(s)}")
                            resource_linked_to[str(s)] = str(p)
                            subject_uri = s


        if len(resource_properties.keys()) > 0 or len(resource_linked_to.keys()) > 0:
            if not 'identifier_in_metadata' in self.data.keys():
                self.data['identifier_in_metadata'] = {}
            if len(resource_properties.keys()) > 0:
                self.data['identifier_in_metadata']['properties'] = resource_properties
            if len(resource_linked_to.keys()) > 0:
                self.data['identifier_in_metadata']['linked_to'] = resource_linked_to

        return subject_uri


    def extract_data_subject(self, 
        g: Any, 
        subject_uri: Optional[List[Any]] = None
    ) -> List[Any]:
        """
        Helper to easily retrieve the subject URI of the data from RDF metadata (RDFLib Graph)

        Parameters:
            g (Graph): RDFLib Graph
            subject_uri: metadata subject URI

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
        # http_props = [p.replace('https://', 'http://') for p in data_props] 
        if not subject_uri:
            subject_uri = [URIRef(str(s)) for s in self.data['alternative_uris']] 
        self.info(f"Searching for the data URI using the following predicates: {', '.join(data_props)}")
        
        data_uris = self.extract_prop(g, preds=data_props, subj=subject_uri)
        
        # Also extract data download URL when possible
        content_props = [
            "https://schema.org/url",
            "https://schema.org/contentUrl", 
            "http://www.w3.org/ns/dcat#downloadURL"
        ]
        extracted_urls = set()
        for data_uri in data_uris:
            if isinstance(data_uri, BNode):
                content_urls = self.extract_prop(g, preds=content_props, subj=data_uri)
                for content_url in content_urls:
                    extracted_urls.add(str(content_url))
            else:
                extracted_urls.add(str(data_uri))

        if not 'data_url' in self.data.keys():
            self.data['content_url'] = []
        self.data['content_url'] = self.data['content_url'] + list(extracted_urls)

        return data_uris



    def response(self) -> JSONResponse:
        """
        Function used to generate the FAIR metric test results as JSON-LD, and return this JSON-LD as HTTP response

        Returns:
            response: HTTP response containing the test results as JSON-LD
        """
        return JSONResponse(self.to_jsonld())


    def to_jsonld(self) -> List[Dict]:
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
    def log(self, 
        log_msg: str, 
        prefix: Optional[str] = None
    ) -> None:
        # Add timestamp?
        log_msg = '[' + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")) + '] ' + log_msg 
        if prefix:
            log_msg = prefix + ' ' + log_msg
        self.comment.append(log_msg)
        # print(log_msg)

    def warn(self, log_msg: str) -> None:
        """
        Log a warning related to the FAIR test execution (add to the comments of the test)

        Parameters:
            log_msg: Message to log
        """
        self.log(log_msg, 'WARN:')
    
    def info(self, log_msg: str) -> None:
        """
        Log an info message related to the FAIR test execution (add to the comments of the test)

        Parameters:
            log_msg: Message to log
        """
        self.log(log_msg, 'INFO:')

    def failure(self, log_msg: str) -> None:
        """
        Log a failure message related to the FAIR test execution (add to the comments of the test and set score to 0)

        Parameters:
            log_msg: Message to log
        """
        self.score = 0
        self.log(log_msg, 'FAILURE:')

    def success(self, log_msg: str) -> None:
        """
        Log a success message related to the FAIR test execution (add to the comments of the test and set score to 1)

        Parameters:
            log_msg: Message to log
        """
        if self.score >= 1:
            self.bonus(log_msg)
        else:
            self.score += 1
            self.log(log_msg, 'SUCCESS:')

    def bonus(self, log_msg: str) -> None:
        self.score_bonus += 1
        self.log(log_msg, 'SUCCESS:')


