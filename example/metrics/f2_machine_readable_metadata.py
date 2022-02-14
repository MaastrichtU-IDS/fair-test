from fair_test import FairTest
import requests


class MetricTest(FairTest):
    metric_path = 'f2-machine-readable-metadata'
    applies_to_principle = 'F2'
    title = 'Metadata is machine-readable'
    description = """This assessment will try to extract metadata from the resource URI:
- Search for structured metadata at the resource URI. 
- Use HTTP requests with content-negotiation (RDF, JSON-LD, JSON), 
- Extract metadata from the HTML landing page using extruct"""
    author = 'https://orcid.org/0000-0002-1501-1082'
    metric_version = '0.1.0'


    def evaluate(self):
        # Check if URL resolve and if redirection
        r = requests.head(self.subject)
        r = requests.get(self.subject)
        r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
        self.info('Successfully resolved ' + self.subject)
        if r.history:
            self.info("Request was redirected to " + r.url + '. Adding as alternative URI')
            self.data['alternative_uris'].append(r.url)
        

        self.info('Checking if machine readable data (e.g. RDF, JSON-LD) can be retrieved using content-negotiation at ' + self.subject)
        g = self.getRDF(self.subject, use_harvester=False)
        if len(g) == 0:
            self.failure('No RDF found at the subject URL provided.')
        else:
            self.success(f'RDF metadata containing {len(g)} triples found at the subject URL provided.')
        
        return self.response()


        # found_content_negotiation = False
        # # self.info('Trying (in this order): ' + ', '.join(check_mime_types))
        # for mime_type in check_mime_types:
        #     try:
        #         r = requests.get(uri, headers={'accept': mime_type})
        #         r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
        #         self.log('Found some metadata when asking for ' + mime_type)
        #         if 'content_negotiation' not in self.data.keys():
        #             self.data['content_negotiation'] = {}
        #         contentType = r.headers['Content-Type'].replace(' ', '').replace(';charset=utf-8', '')
        #         if contentType.startswith('text/html'):
        #             self.log('Content-Type retrieved is text/html, not a machine-readable format', '⏩️')
        #             continue

        #         try:
        #             # If return JSON-LD
        #             self.data['content_negotiation'][contentType] = r.json()

        #             # TODO: use rdflib, instead of this quick fix to get alternative ID from JSON-LD
        #             if 'url' in r.json():
        #                 self.data['alternative_uris'].append(r.json()['url'])
        #                 # url': 'https://doi.pangaea.de/10.1594/PANGAEA.908011
        #         except:
        #             # If returns RDF, such as turtle
        #             self.data['content_negotiation'][contentType] = r.text
        #         found_content_negotiation = True
        #         break
        #     except Exception as e:
        #         self.warn('Could not find metadata with content-negotiation when asking for: ' + mime_type + '. Getting: ' + e.args[0])

        # if found_content_negotiation:
        #     self.success('Found metadata in ' + ', '.join(self.data['content_negotiation'].keys()) + ' format using content-negotiation')
        #     # Parse RDF metadata from content negotiation
        #     for mime_type, rdf_data in self.data['content_negotiation'].items():
        #         g = self.parseRDF(rdf_data, mime_type, msg='content negotiation RDF')
        #         break # Only parse the first RDF metadata file entry
        # else:
        #     self.warn('Could not find metadata using content-negotiation, checking metadata embedded in HTML with extruct')


        # self.info('Checking for metadata embedded in the HTML page returned by the resource URI ' + uri + ' using extruct')
        # try:
        #     get_uri = requests.get(uri, headers={'Accept': 'text/html'})
        #     html_text = html.unescape(get_uri.text)
        #     found_metadata_extruct = False
        #     try:
        #         extracted = extruct.extract(html_text.encode('utf8'))
        #         # Check extruct results:
        #         for extruct_type in extracted.keys():
        #             if extracted[extruct_type]:
        #                 if 'extruct' not in self.data.keys():
        #                     self.data['extruct'] = {}
        #                 if extruct_type == 'dublincore' and extracted[extruct_type] == [{"namespaces": {}, "elements": [], "terms": []}]:
        #                     # Handle case where extruct generate empty dict
        #                     continue
        #                 self.data['extruct'][extruct_type] = extracted[extruct_type]
        #                 found_metadata_extruct = True

        #     except Exception as e:
        #         self.warn('Error when parsing HTML embedded microdata or JSON from ' + uri + ' using extruct. Getting: ' + str(e.args[0]))

        #     if found_metadata_extruct:
        #         self.success('Found embedded metadata in the resource URI HTML page: ' + ', '.join(self.data['extruct'].keys()))
        #     else: 
        #         self.warn('Could not find embedded microdata or JSON in the HTML at ' + uri + ' using extruct')
        # except Exception as e:
        #     self.warn('Error when running extruct on ' + uri + '. Getting: ' + str(e.args[0]))


        return self.response()

