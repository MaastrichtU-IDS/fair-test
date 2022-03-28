from fair_test import FairTest, FairTestEvaluation
import requests
from urllib.parse import urlparse
# from googlesearch import search
# from fastapi import APIRouter, Body, Depends
# from fastapi_utils.cbv import cbv


class MetricTest(FairTest):
    metric_version = '0.1.0'
    metric_path = 'f4-searchable'
    applies_to_principle = 'F4'
    title = 'The resource is indexed in a searchable resource'
    description = """Search for existing metadata about the resource URI in data repositories, such as DataCite, RE3data."""
    author = 'https://orcid.org/0000-0002-1501-1082'
    

    def evaluate(self, eval: FairTestEvaluation):
        datacite_endpoint = 'https://api.datacite.org/repositories'
        re3data_endpoint = 'https://re3data.org/api/beta/repositories'
        datacite_dois_api = 'https://api.datacite.org/dois/'
        # metadata_catalog = https://rdamsc.bath.ac.uk/api/m
        # headers = {"Accept": "application/json"}
        doi = None
        result = urlparse(eval.subject)
        if result.scheme and result.netloc:
            if result.netloc == 'doi.org':
                doi = result.path[1:]
                eval.success('The subject resource URI ' + eval.subject + ' is a DOI')
        else:
            eval.warn('Could not validate the given resource URI ' + eval.subject + ' is a URL')    

        # If DOI: check for metadata in DataCite API
        try:
            if doi:
                eval.info('Checking DataCite API for metadata about the DOI: ' + doi)
                r = requests.get(datacite_dois_api + doi, timeout=10)
                datacite_json = r.json()
                datacite_data = datacite_json['data']['attributes']
                print(datacite_json['data']['attributes'].keys())
                # ['id', 'type', 'attributes', 'relationships']
                if datacite_data:
                    eval.success('Retrieved metadata about ' + doi + ' from DataCite API')
                    eval.data['datacite'] = {}
                    print('datacite_data')
                    print(datacite_data.keys())

                    if 'titles' in datacite_data.keys():
                        eval.data['datacite']['title'] = datacite_data['titles'][0]['title']
                        print(eval.data['datacite']['title'])
                        if not 'title' in eval.data:
                            eval.data['title'] = eval.data['datacite']['title']

                    if 'descriptions' in datacite_data.keys():
                        eval.data['datacite']['description'] = datacite_data['descriptions'][0]['description']
                    
            else:
                eval.warn('DOI could not be found, skipping search in DataCite API')
        except Exception as e:
            eval.warn('Search in DataCite API failed: ' + e.args[0])

        return eval.response() 
        

        # eval.info('Checking RE3data APIs from DataCite API for metadata about ' + uri)
        # p = {'query': 're3data_id:*'}
        # req = requests.get(datacite_endpoint, params=p, headers=headers)
        # print(req.json())


        ## Check google search using the resource title and its alternative URIs
        ## Might be against Google TOS
        # if 'title' in eval.data.keys():
        #     title = eval.data['title']
            
        #     resource_uris = eval.data['alternative_uris']

        #     eval.info('Running Google search for: ' + title)
        #     search_results = list(search(title, tld="co.in", num=20, stop=20, pause=1))
        #     print(search_results)

        #     found_uris = list(set(resource_uris).intersection(search_results))
        #     # if any(i in resource_uris for i in search_results):
        #     if found_uris:
        #         eval.success('Found the resource URI ' + ', '.join(found_uris) + ' when searching on Google for ' + title)
        #     else:
        #         eval.failure('Did not find one of the resource URIs ' + ', '.join(resource_uris) + ' in: '+ ', '.join(search_results))
        # else:
        #     eval.failure('No resource title found, cannot search in google')


    test_test={
        'https://doi.org/10.1594/PANGAEA.908011': 1,
    }