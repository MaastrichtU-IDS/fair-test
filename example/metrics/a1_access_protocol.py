from fair_test import FairTest
from rdflib.namespace import RDFS, XSD, DC, DCTERMS, VOID, OWL, SKOS
import requests


class MetricTest(FairTest):
    metric_path = 'a1-access-protocol'
    applies_to_principle = 'A1'
    title = 'Check Access Protocol'
    description = """The access protocol and authorization (if content restricted).
For the protocol , do an HTTP get on the URL to see if it returns a valid document.
Find information about authorization in metadata"""
    author = 'https://orcid.org/0000-0002-1501-1082'
    metric_version = '0.1.0'


    def evaluate(self):
        self.info(f'Access protocol: check resource URI protocol is resolvable for {self.subject}')
        try:
            r = requests.get(self.subject)
            r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
            self.success('Successfully resolved ' + self.subject)
            if r.history:
                self.info("Request was redirected to " + r.url + '.')
                # self.data['alternative_uris'].append(r.url)

        except Exception as e:
            self.failure(f'Could not resolve {self.subject}. Getting: {e.args[0]}')

        g = self.retrieve_rdf(self.subject)
        self.info('Authorization: checking for dct:accessRights in metadata')
        found_access_rights = False
        access_rights_preds = [DCTERMS.accessRights]
        for pred in access_rights_preds:
            for s, p, accessRights in g.triples((None,  pred, None)):
                self.info(f'Found authorization informations with dcterms:accessRights: {str(accessRights)}')
                # self.data['accessRights'] = str(accessRights)
                found_access_rights = True

        if found_access_rights:
            self.bonus(f'Found dcterms:accessRights in metadata: {str(accessRights)}')
        else:
            self.warn('Could not find dcterms:accessRights information in metadata')
            self.warn(f"Make sure your metadata contains informations about access rights using one of those predicates: {', '.join(access_rights_preds)}")

        return self.response()


    tests={
        'https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972': 1,
        'https://raw.githubusercontent.com/ejp-rd-vp/resource-metadata-schema/master/data/example-rdf/turtle/patientRegistry.ttl': 1,
    }
