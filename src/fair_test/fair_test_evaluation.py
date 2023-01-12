import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlparse

from fastapi.responses import JSONResponse
from pydantic import BaseModel
from rdflib import BNode, Literal, URIRef

from fair_test.config import settings
from fair_test.fair_test_logger import FairTestLogger
from fair_test.metadata_harvester import MetadataHarvester

# pyld is required to parse jsonld with rdflib
# from fastapi import HTTPException
# from fastapi.responses import JSONResponse, PlainTextResponse


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
    subject_url: Optional[str]
    score: int = 0
    score_bonus: int = 0
    date: str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+01:00")
    metric_version: str = "0.1.0"
    data: dict = {}
    id: Optional[str]  # URL of the test results
    logs: FairTestLogger = FairTestLogger()

    def __init__(self, subject: str, metric_path: str) -> None:
        super().__init__()
        self.subject = subject
        self.id = f"{settings.HOST_URL}/metrics/{metric_path}#{quote(str(self.subject))}/result-{self.date}"
        self.subject_url = self.get_url(subject)

        # Add potential alternative URIs for the subject
        if self.subject_url:
            alt_uris = set()
            alt_uris.add(self.subject_url)
            # Add HTTPS/HTTPS counterpart as alternative URIs
            if self.subject_url.startswith("http://"):
                alt_uris.add(self.subject_url.replace("http://", "https://"))
            elif self.subject.startswith("https://"):
                alt_uris.add(self.subject_url.replace("https://", "http://"))

            # Fix to add an alternative URI for doi.org that is commonly used as identifier in the metadata
            parsed_url = urlparse(self.subject_url)
            if parsed_url.netloc and parsed_url.netloc == "doi.org":
                alt_uris.add("http://dx.doi.org/" + parsed_url.path[1:])

            self.data["alternative_uris"] = list(alt_uris)

    class Config:
        arbitrary_types_allowed = True

    @property
    def comment(self) -> List[str]:
        return self.logs.logs

    def get_url(self, id: str) -> Optional[str]:
        """Return the full URL for a given identifiers (e.g. URL, DOI, handle)"""
        harvester = MetadataHarvester()
        url = harvester.get_url(id)
        self.logs.logs += harvester.logs.logs
        return url

    def retrieve_metadata(
        self,
        url: str,
        use_harvester: bool = False,
        harvester_url: str = "https://w3id.org/FAIR_Tests/tests/harvester",
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
        # TODO: implement metadata harvester outside of this class (to be used as API)
        harvester = MetadataHarvester(
            subject=url,
        )
        metadata = harvester.retrieve_metadata(url, use_harvester=use_harvester, harvester_url=harvester_url)
        self.logs.logs += harvester.logs.logs
        return metadata

    def extract_prop(self, g: Any, preds: List[Any], subj: Optional[Any] = None) -> List[Any]:
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
            if str(pred).startswith("http://"):
                check_preds.add(URIRef(str(pred).replace("http://", "https://")))
            elif str(pred).startswith("https://"):
                check_preds.add(URIRef(str(pred).replace("https://", "http://")))

        # self.info(f"Checking properties values for properties: {preds}")
        # if subj:
        #     self.info(f"Checking properties values for subject URI(s): {str(subj)}")
        for pred in list(check_preds):
            if not isinstance(subj, list):
                subj = [subj]
                # test_subjs = [URIRef(str(s)) for s in subj]
            for test_subj in subj:
                for s, p, o in g.triples((test_subj, URIRef(str(pred)), None)):
                    self.info(f"Found a value for a property {str(pred)} => {str(o)}")
                    values.add(o)

        return list(values)

    def extract_metadata_subject(self, g: Any, alt_uris: Optional[List[str]] = None) -> Any:
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
            alt_uris = self.data["alternative_uris"]

        preds_id = [
            "https://purl.org/dc/terms/identifier",
            "https://purl.org/dc/elements/1.1/identifier",
            "https://schema.org/identifier",
            "https://schema.org/sameAs",
            "http://ogp.me/ns#url",
        ]
        all_preds_id = [p.replace("https://", "http://") for p in preds_id] + preds_id
        all_preds_uris = [URIRef(str(s)) for s in all_preds_id]
        resource_properties = {}
        resource_linked_to = {}

        for alt_uri in alt_uris:
            uri_ref = URIRef(str(alt_uri))
            # Search with the subject URI as triple subject
            for s, p, o in g.triples((uri_ref, None, None)):
                self.info(f"Found the subject URI in the metadata: {str(s)}")
                resource_properties[str(p)] = str(o)
                subject_uri = uri_ref

            if not subject_uri:
                # Search with the subject URI as triple object
                for pred in all_preds_uris:
                    for s, p, o in g.triples((None, pred, uri_ref)):
                        self.info(f"Found the subject URI in the metadata: {str(s)}")
                        resource_linked_to[str(s)] = str(p)
                        subject_uri = s

                    if not subject_uri:
                        # Also check when the subject URI defined as Literal
                        for s, p, o in g.triples((None, pred, Literal(str(uri_ref)))):
                            self.info(f"Found the subject URI in the metadata: {str(s)}")
                            resource_linked_to[str(s)] = str(p)
                            subject_uri = s

        if len(resource_properties.keys()) > 0 or len(resource_linked_to.keys()) > 0:
            if not "identifier_in_metadata" in self.data.keys():
                self.data["identifier_in_metadata"] = {}
            if len(resource_properties.keys()) > 0:
                self.data["identifier_in_metadata"]["properties"] = resource_properties
            if len(resource_linked_to.keys()) > 0:
                self.data["identifier_in_metadata"]["linked_to"] = resource_linked_to

        return subject_uri

    def extract_data_subject(self, g: Any, subject_uri: Optional[List[Any]] = None) -> List[Any]:
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
            "https://purl.obolibrary.org/obo/IAO_0000136",
        ]
        # http_props = [p.replace('https://', 'http://') for p in data_props]
        if not subject_uri:
            subject_uri = [URIRef(str(s)) for s in self.data["alternative_uris"]]
        self.info(f"Searching for the data URI using the following predicates: {', '.join(data_props)}")

        data_uris = self.extract_prop(g, preds=data_props, subj=subject_uri)

        # Also extract data download URL when possible
        content_props = [
            "https://schema.org/url",
            "https://schema.org/contentUrl",
            "http://www.w3.org/ns/dcat#downloadURL",
        ]
        self.info(
            f"Checking if the data URI point to a download URL using one of the following predicates: {', '.join(content_props)}"
        )
        extracted_urls = set()
        for data_uri in data_uris:
            if isinstance(data_uri, BNode):
                content_urls = self.extract_prop(g, preds=content_props, subj=data_uri)
                for content_url in content_urls:
                    extracted_urls.add(str(content_url))
            else:
                extracted_urls.add(str(data_uri))

        if not "data_url" in self.data.keys():
            self.data["content_url"] = []
        self.data["content_url"] = self.data["content_url"] + list(extracted_urls)

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
                "@type": ["http://fairmetrics.org/resources/metric_evaluation_result"],
                "http://purl.obolibrary.org/obo/date": [
                    {
                        "@value": self.date,
                        "@type": "http://www.w3.org/2001/XMLSchema#date",
                    }
                ],
                "http://schema.org/softwareVersion": [
                    {
                        "@value": self.metric_version,
                        "@type": "http://www.w3.org/2001/XMLSchema#float",
                    }
                ],
                "http://schema.org/comment": [{"@value": "\n\n".join(self.comment), "@language": "en"}],
                "http://semanticscience.org/resource/SIO_000332": [{"@value": str(self.subject), "@language": "en"}],
                "http://semanticscience.org/resource/SIO_000300": [
                    {
                        "@value": float(self.score),
                        "@type": "http://www.w3.org/2001/XMLSchema#float",
                    }
                ],
                "http://semanticscience.org/resource/metadata": self.data,
            }
        ]

    # Logging utilities
    def log(self, log_msg: str, prefix: Optional[str] = None) -> None:
        self.logs.log(log_msg, prefix)

    def warn(self, log_msg: str) -> None:
        """
        Log a warning related to the FAIR test execution (add to the comments of the test)

        Parameters:
            log_msg: Message to log
        """
        self.logs.warn(log_msg)

    def info(self, log_msg: str) -> None:
        """
        Log an info message related to the FAIR test execution (add to the comments of the test)

        Parameters:
            log_msg: Message to log
        """
        self.logs.info(log_msg)

    def failure(self, log_msg: str) -> None:
        """
        Log a failure message related to the FAIR test execution (add to the comments of the test and set score to 0)

        Parameters:
            log_msg: Message to log
        """
        self.score = 0
        self.logs.failure(log_msg)

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
            self.logs.success(log_msg)

    def bonus(self, log_msg: str) -> None:
        self.score_bonus += 1
        self.logs.success(log_msg)
