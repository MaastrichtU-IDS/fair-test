from fair_test import FairTest
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


    def evaluate(self):        
        found_license = False
        # Issue with extracting license from some URIs, such as https://www.uniprot.org/uniprot/P51587
        # Getting a URI that is not really the license as output
        g = self.retrieve_rdf(self.subject, use_harvester=True, harvester_url='http://wrong-url-for-testing')
        if len(g) == 0:
            self.failure('No RDF found at the subject URL provided.')
            return self.response()
        else:
            self.info(f'RDF metadata containing {len(g)} triples found at the subject URL provided.')

        # TODO: check DataCite too
        license_uris = [DCTERMS.license, URIRef('https://schema.org/license'), URIRef('http://www.w3.org/1999/xhtml/vocab#license')]
        self.info('Checking for license in RDF metadata.')
        # TODO: use self.data['alternative_uris']
        # Get license from RDF metadata
        self.info(f'Check LICENSE PROPS {license_uris}')
        # data_res = self.extract_prop(g, license_uris, self.data['alternative_uris'])
        
        # Added for better test coverage:
        test_subjects = [None, self.subject, self.subject.replace('http://', 'https://').replace('https://', 'http://')]
        data_res = self.extract_prop(g, license_uris, test_subjects)
        data_res = self.extract_prop(g, license_uris)

        if len(list(data_res)) < 1:
            self.failure("Could not find data for the metadata. Searched for the following predicates: " + ', '.join(license_uris))

        for license_value in data_res:
            self.log(f'Found license: {str(license_value)}')
            if isinstance(license_value, list):
                self.data['license'] = str(license_value[0])
            else:
                self.data['license'] = str(license_value)
            found_license = True

        if found_license:
            self.success('Found license in metadata')
        else:
            self.failure('Could not find license information in metadata')


        if 'license' in self.data.keys():
            self.info('Check if license is approved by the Open Source Initiative, in the SPDX licenses list')
            # https://github.com/vemonet/fuji/blob/master/fuji_server/helper/preprocessor.py#L229
            spdx_licenses_url = 'https://raw.github.com/spdx/license-list-data/master/json/licenses.json'
            spdx_licenses = requests.get(spdx_licenses_url).json()['licenses']
            for license in spdx_licenses:
                if self.data['license'] in license['seeAlso']:
                    if license['isOsiApproved'] == True:
                        self.bonus('License approved by the Open Source Initiative (' + str(self.data['license']) + ')')

        return self.response()


    test_test={
        'https://doi.org/10.1594/PANGAEA.908011': 1,
    }