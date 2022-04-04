from fair_test import FairTest, FairTestEvaluation
from rdflib.namespace import RDFS, XSD, DC, DCTERMS, VOID, OWL, SKOS
import requests
from urllib.parse import urlparse


class MetricTest(FairTest):
    metric_path = 'a1-metadata-protocol'
    applies_to_principle = 'A1.1'
    title = 'Metadata uses an open free protocol for metadata retrieval'
    description = """Metadata may be retrieved by an open and free protocol. Tests metadata GUID for its resolution protocol. Accept URLs."""
    topics = ['metadata']
    author = 'https://orcid.org/0000-0002-1501-1082'
    metric_version = '0.1.0'
    test_test={
        'https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972': 1,
        'https://raw.githubusercontent.com/ejp-rd-vp/resource-metadata-schema/master/data/example-rdf/turtle/patientRegistry.ttl': 1,
        'Wrong entry': 0,
    }


    def evaluate(self, eval: FairTestEvaluation):
        # TODO: use https://pythonhosted.org/IDUtils
        
        eval.info('Checking if the given resource URI ' + eval.subject + ' is a valid URL using urllib.urlparse')
        result = urlparse(eval.subject)
        if result.scheme and result.netloc:
            # Get URI protocol retrieved in f1_1_assess_unique_identifier
            eval.data['uri_protocol'] = result.scheme
            eval.data['uri_location'] = result.netloc
            if result.netloc == 'doi.org':
                eval.data['uri_doi'] = result.path[1:]
            eval.success('Validated the given resource URI ' + eval.subject + ' is a URL')
        else:
            eval.failure('Could not validate the given resource URI ' + eval.subject + ' is a URL')    

        return eval.response()
