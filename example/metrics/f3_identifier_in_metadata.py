from fair_test import FairTest, FairTestEvaluation
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


    def evaluate(self, eval: FairTestEvaluation):
        # alt_uris = [eval.subject, eval.subject.lower()]
        # # Add alternative URIs to increase the chances to find the ID
        # if eval.subject.startswith('http://'):
        #     alt_uris.append(eval.subject.replace('http://', 'https://'))
        #     alt_uris.append(eval.subject.replace('http://', 'https://').lower())
        # elif eval.subject.startswith('https://'):
        #     alt_uris.append(eval.subject.replace('https://', 'http://'))
        #     alt_uris.append(eval.subject.replace('http://', 'https://').lower())
        
        # # Quick fix to add an alternative URIs for doi.org that is used as identifier in the metadata
        # result = urlparse(eval.subject)
        # if result.scheme and result.netloc:
        #     if result.netloc == 'doi.org':
        #         alt_uris.append(eval.subject.replace('https://doi.org/', 'http://dx.doi.org/'))
        #         # doi = result.path[1:]
        #         eval.info('The subject resource URI ' + eval.subject + ' is a DOI')


        g = eval.retrieve_rdf(eval.subject, use_harvester=True)
        if len(g) == 0:
            eval.failure('No RDF found at the subject URL provided.')
            return eval.response()
        else:
            eval.info(f'RDF metadata containing {len(g)} triples found at the subject URL provided.')

        # FDP specs: https://github.com/FAIRDataTeam/FAIRDataPoint-Spec/blob/master/spec.md
        # Stats for KG: https://www.w3.org/TR/hcls-dataset

        eval.info(f"Checking RDF metadata to find links to all the alternative identifiers: <{'>, <'.join(eval.data['alternative_uris'])}>")
        found_link = False
        for alt_uri in eval.data['alternative_uris']:
            uri_ref = URIRef(alt_uri)
            resource_properties = {}
            resource_linked_to = {}
            eval.data['identifier_in_metadata'] = {}
            for p, o in g.predicate_objects(uri_ref):
                found_link = True
                resource_properties[str(p)] = str(o)
            eval.data['identifier_in_metadata']['properties'] = resource_properties
            for s, p in g.subject_predicates(uri_ref):
                found_link = True
                resource_linked_to[str(s)] = str(p)
            eval.data['identifier_in_metadata']['linked_to'] = resource_linked_to

            # eval.data['identifier_in_metadata'] = {
            #     'properties': resource_properties,
            #     'linked_to': resource_linked_to,
            # }
            # print('identifier_in_metadata')
            # print(eval.data['identifier_in_metadata'])

            # Try to extract some metadata from the parsed RDF
            title_preds = [ DC.title, DCTERMS.title, RDFS.label, URIRef('http://schema.org/name')]
            titles = eval.extract_prop(g, title_preds, eval.data['alternative_uris'])
            if len(titles) > 0:
                eval.log(f"Found titles: {' ,'.join(titles)}")
                eval.data['title'] = titles


            description_preds = [ DCTERMS.description, URIRef('http://schema.org/description')]
            descriptions = eval.extract_prop(g, description_preds, eval.data['alternative_uris'])
            if len(descriptions) > 0:
                eval.log(f"Found descriptions: {' ,'.join(descriptions)}")
                eval.data['description'] = descriptions

            date_created_preds = [ DCTERMS.created, URIRef('http://schema.org/dateCreated'), URIRef('http://schema.org/datePublished')]
            dates = eval.extract_prop(g, date_created_preds, eval.data['alternative_uris'])
            if len(dates) > 0:
                eval.log(f"Found created date: {' ,'.join(dates)}")
                eval.data['created'] = dates


            if found_link:
                eval.success('Found properties/links for the URI ' + alt_uri + ' in the metadata: ' 
                    + ', '.join(list(eval.data['identifier_in_metadata']['properties'].keys()) + list(eval.data['identifier_in_metadata']['linked_to'].keys()))
                )
                break
            else: 
                eval.failure('Could not find links to the resource URI ' + alt_uri + ' in the RDF metadata')


        return eval.response()

    test_test={
        'https://doi.org/10.1594/PANGAEA.908011': 1,
    }