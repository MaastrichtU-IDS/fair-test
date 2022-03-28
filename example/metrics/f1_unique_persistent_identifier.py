from fair_test import FairTest, FairTestEvaluation
from urllib.parse import urlparse
import requests


class MetricTest(FairTest):
    metric_path = 'f1-unique-persistent-id'
    applies_to_principle = 'F1'
    title = 'Resource identifier is unique and persistent'
    description = 'Check if the identifier of the resource is unique (HTTP) and persistent (some HTTP domains)'
    author = 'https://orcid.org/0000-0002-1501-1082'
    metric_version = '0.1.0'


    def evaluate(self, eval: FairTestEvaluation):
        # TODO: use https://pythonhosted.org/IDUtils
        accepted_persistent = ['doi.org', 'purl.org', 'identifiers.org', 'w3id.org']
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


        # Check if URL resolve and if redirection
        r = requests.head(eval.subject)
        r = requests.get(eval.subject)
        r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
        eval.log('Successfully resolved ' + eval.subject, '☑️')
        if r.history:
            eval.log("Request was redirected to " + r.url + '. Adding as alternative URI')
            eval.data['alternative_uris'].append(r.url)
        

        eval.info('Check if the given resource URI ' + eval.subject + ' use a persistent URI, one of: ' + ', '.join(accepted_persistent))
        if eval.data['uri_location'] in accepted_persistent:
            # Checking URI location extracted by f1_1_assess_unique_identifier
            # eval.score += 1
            eval.success('Validated the given resource URI ' + eval.subject + ' is a persistent URL')
        else:
            r = urlparse(eval.subject)
            if r.netloc and r.netloc in accepted_persistent:
                eval.success('Validated the given resource URI ' + eval.subject + ' is a persistent URL')
            else:
                eval.failure('The given resource URI ' + eval.subject + ' is not considered a persistent URL')

        # Quick fix to add an alternative URI for doi.org that is used as identifier in the metadata
        if eval.data['uri_location'] == 'doi.org':
            eval.data['alternative_uris'].append(eval.subject.replace('https://doi.org/', 'http://dx.doi.org/'))
            eval.data['alternative_uris'].append(eval.subject.lower())

        return eval.response()


    test_test={
        'https://raw.githubusercontent.com/ejp-rd-vp/resource-metadata-schema/master/data/example-rdf/turtle/patientRegistry.ttl': 0,
        # FAIR Data Point failing occasionally
        # 'https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972': 1,
    }