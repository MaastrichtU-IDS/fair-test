from fastapi.testclient import TestClient
from fair_test import FairTestAPI
import yaml

app = FairTestAPI(metrics_folder_path='example/metrics')

endpoint = TestClient(app)

eval_list = [
    # a1-access-protocol
    {
        'metric_id': 'a1-access-protocol',
        'subject': 'https://raw.githubusercontent.com/ejp-rd-vp/resource-metadata-schema/master/data/example-rdf/turtle/patientRegistry.ttl',
        'score': 1,
    },
    # {
    #     'metric_id': 'a1-access-protocol',
    #     'subject': 'https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972',
    #     'score': 1,
    # },
    # f1-unique-persistent-id
    {
        'metric_id': 'f1-unique-persistent-id',
        'subject': 'https://raw.githubusercontent.com/ejp-rd-vp/resource-metadata-schema/master/data/example-rdf/turtle/patientRegistry.ttl',
        'score': 0,
    },
    # {
    #     'metric_id': 'f1-unique-persistent-id',
    #     'subject': 'https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972',
    #     'score': 1,
    # },
    # f2-machine-readable-metadata
    {
        'metric_id': 'f2-machine-readable-metadata',
        'subject': 'https://doi.org/10.1594/PANGAEA.908011',
        'score': 1,
    },
    # {
    #     'metric_id': 'f2-machine-readable-metadata',
    #     'subject': 'https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972',
    #     'score': 1,
    # },
    {
        'metric_id': 'f2-machine-readable-metadata',
        'subject': 'http://example.com',
        'score': 0,
    },
]


def test_get_yaml():
    metrics_id_to_test = set()
    for eval in eval_list:
        metrics_id_to_test.add(eval['metric_id'])
    for metric_id in list(metrics_id_to_test):
        r = endpoint.get(f"/tests/{metric_id}")
        # print(r.text)
        assert r.status_code == 200
        api_yaml = yaml.load(r.text, Loader=yaml.FullLoader)
        assert api_yaml['info']['title']
        assert api_yaml['info']['x-applies_to_principle']
        assert api_yaml['info']['x-tests_metric']


def test_post_eval():
    for eval in eval_list:
        r = endpoint.post(f"/tests/{eval['metric_id']}",
            json={ 'subject': eval['subject'] },
            headers={"Accept": "application/json"}
        )
        print(f"Test posting subject <{eval['subject']}> to {eval['metric_id']} (expect {eval['score']})")
        assert r.status_code == 200
        res = r.json()
        # Check score:
        assert res[0]['http://semanticscience.org/resource/SIO_000300'][0]['@value'] == eval['score']


def test_bad_request():
    response = endpoint.post(f'/tests/a1-access-protocol', 
        json={'subject': ''},
        headers={'accept': 'application/json'})
    print(response.status_code)
    assert response.status_code == 422


def test_404():
    response = endpoint.get(f'/dont-exist', 
        headers={'accept': 'application/json'})
    assert response.status_code == 404


def test_redirect():
    response = endpoint.get('/')
    assert response.status_code == 200
