from fair_test import FairTest, FairTestEvaluation
import json
import rdflib
import requests
import yaml
# JSON-LD workaround 
# from pyld import jsonld
# from rdflib import ConjunctiveGraph
# from rdflib.serializer import Serializer


class MetricTest(FairTest):
    metric_path = 'i1-metadata-knowledge-representation-weak'
    applies_to_principle = 'I1'
    title = 'Metadata uses a formal knowledge representation language (weak)'
    description = """Maturity Indicator to test if the metadata uses a formal language broadly applicable for knowledge representation.
This particular test takes a broad view of what defines a 'knowledge representation language'; in this evaluation, anything that can be represented as structured data will be accepted"""
    author = 'https://orcid.org/0000-0002-1501-1082'
    metric_version = '0.1.0'


    def evaluate(self, eval: FairTestEvaluation):        
        # https://github.com/vemonet/fuji/blob/master/fuji_server/helper/preprocessor.py#L190
        g = eval.retrieve_rdf(eval.subject)
        if len(g) > 1:
            eval.success('Successfully parsed the RDF metadata retrieved with content negotiation. It contains ' + str(len(g)) + ' triples')
        else:
            eval.warn('No RDF metadata found, searching for JSON')
            try:
                r = requests.get(eval.subject, headers={'accept': 'application/json'})
                metadata = r.json()
                eval.success('Successfully found and parsed JSON metadata: ' + json.dumps(metadata))
            except:
                eval.warn('No JSON metadata found, searching for YAML')
                try:
                    r = requests.get(eval.subject, headers={'accept': 'application/json'})
                    metadata = yaml.load(r.text, Loader=yaml.FullLoader)
                    eval.success('Successfully found and parsed YAML metadata: ' + json.dumps(r))
                except:
                    eval.failure('No YAML metadata found')
            
        return eval.response()

