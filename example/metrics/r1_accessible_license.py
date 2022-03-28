from fair_test import FairTest, FairTestEvaluation
import requests
from rdflib import Literal, RDF, URIRef
from rdflib.namespace import RDFS, XSD, DC, DCTERMS, VOID, OWL, SKOS, FOAF


class MetricTest(FairTest):
    metric_path = 'r1-accessible-license'
    applies_to_principle = 'R1'
    title = 'Check accessible Usage License'
    description = """The existence of a license document, for BOTH (independently) the data and its associated metadata, and the ability to retrieve those documents
Resolve the licenses IRI"""
    author = 'https://orcid.org/0000-0002-1501-1082'
    metric_version = '0.1.0'


    def evaluate(self, eval: FairTestEvaluation):        
        found_license = False
        # Issue with extracting license from some URIs, such as https://www.uniprot.org/uniprot/P51587
        # Getting a URI that is not really the license as output
        g = eval.retrieve_rdf(eval.subject, use_harvester=True, harvester_url='http://wrong-url-for-testing')
        if len(g) == 0:
            eval.failure('No RDF found at the subject URL provided.')
            return eval.response()
        else:
            eval.info(f'RDF metadata containing {len(g)} triples found at the subject URL provided.')

        # TODO: check DataCite too
        license_uris = [DCTERMS.license, URIRef('https://schema.org/license'), URIRef('http://www.w3.org/1999/xhtml/vocab#license')]
        eval.info('Checking for license in RDF metadata.')
        # TODO: use eval.data['alternative_uris']
        # Get license from RDF metadata
        eval.info(f'Check LICENSE PROPS {license_uris}')
        # data_res = eval.extract_prop(g, license_uris, eval.data['alternative_uris'])
        
        # Added for better test coverage:
        test_subjects = [None, eval.subject, eval.subject.replace('http://', 'https://').replace('https://', 'http://')]
        data_res = eval.extract_prop(g, license_uris, test_subjects)
        data_res = eval.extract_prop(g, license_uris)

        if len(list(data_res)) < 1:
            eval.failure("Could not find data for the metadata. Searched for the following predicates: " + ', '.join(license_uris))

        for license_value in data_res:
            eval.log(f'Found license: {str(license_value)}')
            if isinstance(license_value, list):
                eval.data['license'] = str(license_value[0])
            else:
                eval.data['license'] = str(license_value)
            found_license = True

        if found_license:
            eval.success('Found license in metadata')
        else:
            eval.failure('Could not find license information in metadata')


        if 'license' in eval.data.keys():
            eval.info('Check if license is approved by the Open Source Initiative, in the SPDX licenses list')
            # https://github.com/vemonet/fuji/blob/master/fuji_server/helper/preprocessor.py#L229
            spdx_licenses_url = 'https://raw.github.com/spdx/license-list-data/master/json/licenses.json'
            spdx_licenses = requests.get(spdx_licenses_url).json()['licenses']
            for license in spdx_licenses:
                if eval.data['license'] in license['seeAlso']:
                    if license['isOsiApproved'] == True:
                        eval.bonus('License approved by the Open Source Initiative (' + str(eval.data['license']) + ')')

        return eval.response()


    test_test={
        'https://doi.org/10.1594/PANGAEA.908011': 1,
    }