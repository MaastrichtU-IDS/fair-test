from fair_test import FairTest
from rdflib import Literal, RDF, URIRef
from rdflib.namespace import RDFS, XSD, DC, DCTERMS, VOID, OWL, SKOS, FOAF
from urllib.parse import urlparse


class MetricTest(FairTest):
    metric_path = 'f3-id-in-metadata'
    applies_to_principle = 'F3'
    title = 'Resource Identifier is in Metadata'
    description = """Whether the metadata document contains the globally unique and persistent identifier for the digital resource.
Parse the metadata to search for the given digital resource GUID.
If found, retrieve informations about this resource (title, description, date created, etc)"""
    author = 'https://orcid.org/0000-0002-1501-1082'
    metric_version = '0.1.0'


    def evaluate(self):
        alt_uris = [self.subject, self.subject.lower()]
        # Add alternative URIs to increase the chances to find the ID
        if self.subject.startswith('http://'):
            alt_uris.append(self.subject.replace('http://', 'https://'))
            alt_uris.append(self.subject.replace('http://', 'https://').lower())
        elif self.subject.startswith('https://'):
            alt_uris.append(self.subject.replace('https://', 'http://'))
            alt_uris.append(self.subject.replace('http://', 'https://').lower())
        
        # Quick fix to add an alternative URIs for doi.org that is used as identifier in the metadata
        result = urlparse(self.subject)
        if result.scheme and result.netloc:
            if result.netloc == 'doi.org':
                alt_uris.append(self.subject.replace('https://doi.org/', 'http://dx.doi.org/'))
                # doi = result.path[1:]
                self.info('The subject resource URI ' + self.subject + ' is a DOI')


        g = self.getRDF(self.subject)
        if len(g) == 0:
            self.failure('No RDF found at the subject URL provided.')
            return self.response()
        else:
            self.info(f'RDF metadata containing {len(g)} triples found at the subject URL provided.')

        # FDP specs: https://github.com/FAIRDataTeam/FAIRDataPoint-Spec/blob/master/spec.md
        # Stats for KG: https://www.w3.org/TR/hcls-dataset

        self.info(f"Checking RDF metadata to find links to all the alternative identifiers: <{'>, <'.join(alt_uris)}>")
        found_link = False
        for alt_uri in alt_uris:
            uri_ref = URIRef(alt_uri)
            resource_properties = {}
            resource_linked_to = {}
            self.data['identifier_in_metadata'] = {}
            for p, o in g.predicate_objects(uri_ref):
                found_link = True
                resource_properties[str(p)] = str(o)
            self.data['identifier_in_metadata']['properties'] = resource_properties
            for s, p in g.subject_predicates(uri_ref):
                found_link = True
                resource_linked_to[str(s)] = str(p)
            self.data['identifier_in_metadata']['linked_to'] = resource_linked_to

            # self.data['identifier_in_metadata'] = {
            #     'properties': resource_properties,
            #     'linked_to': resource_linked_to,
            # }
            # print('identifier_in_metadata')
            # print(self.data['identifier_in_metadata'])

            # Try to extract some metadata from the parsed RDF
            # title_preds = [ DC.title, DCTERMS.title, RDFS.label, URIRef('http://schema.org/name')]
            # eval, g = self.extract_property('resource_title', title_preds, eval, g)

            # description_preds = [ DCTERMS.description, URIRef('http://schema.org/description')]
            # eval, g = self.extract_property('resource_description', description_preds, eval, g)

            # date_created_preds = [ DCTERMS.created, URIRef('http://schema.org/dateCreated'), URIRef('http://schema.org/datePublished')]
            # eval, g = self.extract_property('date_created', date_created_preds, eval, g)

            if found_link:
                self.success('Found properties/links for the URI ' + alt_uri + ' in the metadata: ' 
                    + ', '.join(list(self.data['identifier_in_metadata']['properties'].keys()) + list(self.data['identifier_in_metadata']['linked_to'].keys()))
                )
                break
            else: 
                self.failure('Could not find links to the resource URI ' + alt_uri + ' in the RDF metadata')


        return self.response()

