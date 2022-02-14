from fair_test import FairTest
from urllib.parse import urlparse
import requests


class MetricTest(FairTest):
    metric_path = 'f1-unique-persistent-id'
    applies_to_principle = 'F1'
    title = 'Resource identifier is unique and persistent'
    description = 'Check if the identifier of the resource is unique (HTTP) and persistent (some HTTP domains)'
    author = 'https://orcid.org/0000-0002-1501-1082'
    metric_version = '0.1.0'


    def evaluate(self):
        # TODO: use https://pythonhosted.org/IDUtils
        accepted_persistent = ['doi.org', 'purl.org', 'identifiers.org', 'w3id.org']
        self.info('Checking if the given resource URI ' + self.subject + ' is a valid URL using urllib.urlparse')
        result = urlparse(self.subject)
        if result.scheme and result.netloc:
            # Get URI protocol retrieved in f1_1_assess_unique_identifier
            self.data['uri_protocol'] = result.scheme
            self.data['uri_location'] = result.netloc
            if result.netloc == 'doi.org':
                self.data['uri_doi'] = result.path[1:]
            self.success('Validated the given resource URI ' + self.subject + ' is a URL')
        else:
            self.failure('Could not validate the given resource URI ' + self.subject + ' is a URL')    


        # Check if URL resolve and if redirection
        r = requests.head(self.subject)
        r = requests.get(self.subject)
        r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
        self.log('Successfully resolved ' + self.subject, '☑️')
        if r.history:
            self.log("Request was redirected to " + r.url + '. Adding as alternative URI')
            self.data['alternative_uris'].append(r.url)
        

        self.info('Check if the given resource URI ' + self.subject + ' use a persistent URI, one of: ' + ', '.join(accepted_persistent))
        if self.data['uri_location'] in accepted_persistent:
            # Checking URI location extracted by f1_1_assess_unique_identifier
            # self.score += 1
            self.success('Validated the given resource URI ' + self.subject + ' is a persistent URL')
        else:
            r = urlparse(self.subject)
            if r.netloc and r.netloc in accepted_persistent:
                self.success('Validated the given resource URI ' + self.subject + ' is a persistent URL')
            else:
                self.failure('The given resource URI ' + self.subject + ' is not considered a persistent URL')

        # Quick fix to add an alternative URI for doi.org that is used as identifier in the metadata
        if self.data['uri_location'] == 'doi.org':
            self.data['alternative_uris'].append(self.subject.replace('https://doi.org/', 'http://dx.doi.org/'))
            self.data['alternative_uris'].append(self.subject.lower())

        return self.response()
