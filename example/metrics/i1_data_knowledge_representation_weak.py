from fair_test import FairTest
import json
import rdflib
import requests
import yaml
# JSON-LD workaround 
# from pyld import jsonld
# from rdflib import ConjunctiveGraph
# from rdflib.serializer import Serializer


class MetricTest(FairTest):
    metric_path = 'i1-data-knowledge-representation-weak'
    applies_to_principle = 'I1'
    title = 'Data uses a formal knowledge representation language (weak)'
    description = """Maturity Indicator to test if the data uses a formal language broadly applicable for knowledge representation.
This particular test takes a broad view of what defines a 'knowledge representation language'; in this evaluation, anything that can be represented as structured data will be accepted"""
    author = 'https://orcid.org/0000-0002-1501-1082'
    metric_version = '0.1.0'


    def evaluate(self):        
        g = self.retrieve_rdf(self.subject)
        if len(g) > 1:
            self.info(f'Successfully found and parsed RDF metadata. It contains {str(len(g))} triples')

        # Retrieve URI of the data in the RDF metadata
        data_res = self.extract_data_uri(g)
        if len(data_res) < 1:
            self.failure("Could not find data URI in the metadata.")

        # Check if structured data can be found at the data URI
        for value in data_res:
            self.info(f'Found data URI: {value}. Try retrieving RDF')
            data_g = self.retrieve_rdf(value)
            if len(data_g) > 1:
                self.info(f'Successfully retrieved RDF for the data URI: {value}. It contains {str(len(g))} triples')
                self.success(f'Successfully found and parsed RDF data for {value}')

            else:
                self.warn(f'No RDF data found for {value}, searching for JSON')
                try:
                    r = requests.get(value, headers={'accept': 'application/json'})
                    metadata = r.json()
                    self.success(f'Successfully found and parsed JSON data for {value}: ' + json.dumps(metadata))
                except:
                    self.warn(f'No JSON metadata found for {value}, searching for YAML')
                    try:
                        r = requests.get(value, headers={'accept': 'application/json'})
                        metadata = yaml.load(r.text, Loader=yaml.FullLoader)
                        self.success(f'Successfully found and parsed YAML data for {value}: ' + json.dumps(r))
                    except:
                        self.failure(f'No YAML metadata found for {value}')
            
        return self.response()

    test_test={
        'https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972': 1,
        'https://doi.org/10.1594/PANGAEA.908011': 0,
    }
