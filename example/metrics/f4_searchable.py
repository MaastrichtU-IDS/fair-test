from fair_test import FairTest, FairTestEvaluation
import requests
from urllib.parse import urlparse
import json
from duckduckgo_search import ddg
# from fastapi import APIRouter, Body, Depends
# from fastapi_utils.cbv import cbv


class MetricTest(FairTest):
    metric_version = '0.1.0'
    metric_path = 'f4-searchable'
    applies_to_principle = 'F4'
    title = 'The resource is indexed in a searchable resource'
    description = """Search for existing metadata about the resource URI in data repositories, such as DataCite, RE3data."""
    author = 'https://orcid.org/0000-0002-1501-1082'
    test_test={
        'https://doi.org/10.1594/PANGAEA.908011': 1,
        'Wrong entry': 0,
    }
    

    def evaluate(self, eval: FairTestEvaluation):
        datacite_endpoint = 'https://api.datacite.org/repositories'
        re3data_endpoint = 'https://re3data.org/api/beta/repositories'
        datacite_dois_api = 'https://api.datacite.org/dois/'
        # metadata_catalog = https://rdamsc.bath.ac.uk/api/m
        headers = {"Accept": "application/json"}
        doi = None
        result = urlparse(eval.subject)
        if result.scheme and result.netloc:
            if result.netloc == 'doi.org':
                doi = result.path[1:]
                eval.info('The subject resource URI ' + eval.subject + ' is a DOI')
        else:
            eval.warn('Could not validate the given resource URI ' + eval.subject + ' is a URL')    

        # If DOI: check for metadata in DataCite API
        try:
            if doi:
                # if self.subject.startswith('https://doi.org/') or self.subject.startswith('http://doi.org/'):
                eval.info('Checking DataCite API for metadata about the DOI: ' + doi)
                r = requests.get(datacite_dois_api + doi, timeout=10)
                datacite_json = r.json()
                datacite_data = datacite_json['data']['attributes']
                # print(datacite_json['data']['attributes'].keys())
                # ['id', 'type', 'attributes', 'relationships']
                if datacite_data:
                    eval.success('Found ' + doi + ' in DataCite')
                    eval.data['datacite'] = {}
                    # print('datacite_data')
                    # print(datacite_data.keys())

                    if 'titles' in datacite_data.keys():
                        eval.data['datacite']['title'] = datacite_data['titles'][0]['title']
                        # print(eval.data['datacite']['title'])
                        if not 'title' in eval.data:
                            eval.data['title'] = [eval.data['datacite']['title']]

                    if 'descriptions' in datacite_data.keys():
                        eval.data['datacite']['description'] = datacite_data['descriptions'][0]['description']
                    
            else:
                eval.warn('DOI could not be found, skipping search in DataCite API')
        except Exception as e:
            eval.warn('Search in DataCite API failed: ' + e.args[0])        

        # eval.info('Checking RE3data APIs from DataCite API for metadata about ' + uri)
        # p = {'query': 're3data_id:*'}
        # req = requests.get(datacite_endpoint, params=p, headers=headers)
        # print(req.json())

        ## Check DuckDuckGo search using the resource title and its alternative URIs
        if 'title' in eval.data.keys() and len(eval.data['title']) > 0:
            title = eval.data['title'][0]

            resource_uris = eval.data['alternative_uris']
            eval.info('Running search in DuckDuckGo for: ' + title)
            try:
                # ddg(keywords, region='wt-wt', safesearch='Moderate', time=None, max_results=50):
                search_results = ddg(title, region='wt-wt', max_results=80)
                # search_results = list(search(title, tld="co.in", num=20, stop=20, pause=1))
                # print(json.dumps(search_results, indent=2))
                uris_found = [s['href'] for s in search_results] 

                matching_uris = list(set(resource_uris).intersection(uris_found))
                # if any(i in resource_uris for i in search_results):
                if matching_uris:
                    eval.success('Found the resource URI ' + ', '.join(matching_uris) + ' when searching in popular Search Engines for ' + title)
                else:
                    eval.warn('Did not find one of the resource URIs ' + ', '.join(resource_uris) + ' in the URIs found: '+ ', '.join(uris_found))
                    eval.warn(f"Resource not found when searching in DuckDuckGo for {title}")
            except:
                eval.warn('Error running DuckDuckGo search')
        else:
            eval.warn('No resource title found, cannot search in Search Engine')

        return eval.response()

    # Bing requires an API key
    # bing_apikey = os.getenv('APIKEY_BING_SEARCH')
    # headers = {"Ocp-Apim-Subscription-Key": bing_apikey}
    # params = {"q": title, "textDecorations": True, "textFormat": "HTML"}
    # response = requests.get(search_url, headers=headers, params=params)
    # response.raise_for_status()
    # search_results = response.json()