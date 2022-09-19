import requests

from fair_test import FairTest, FairTestEvaluation


class MetricTest(FairTest):
    metric_path = "a1-metadata-protocol"
    applies_to_principle = "A1.1"
    title = "Metadata uses an open free protocol for metadata retrieval"
    description = """Metadata may be retrieved by an open and free protocol. Tests metadata GUID for its resolution protocol. Accept URLs."""
    topics = ["metadata"]
    author = "https://orcid.org/0000-0002-1501-1082"
    metric_version = "0.1.0"
    test_test = {
        "https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972": 1,
        "https://raw.githubusercontent.com/ejp-rd-vp/resource-metadata-schema/master/data/example-rdf/turtle/patientRegistry.ttl": 1,
        "10.1016/j.jbi.2008.03.004": 1,
        "doi:10.1016/j.jbi.2008.03.004": 1,
        "Wrong entry": 0,
    }

    def evaluate(self, eval: FairTestEvaluation):

        eval.info(
            f"Checking if the resource identifier {eval.subject} uses a valid protocol, such as URL, DOI, or handle"
        )
        subject_url = eval.get_url(eval.subject)
        if not subject_url:
            eval.failure(
                f"The resource {eval.subject} does not use a valid identifier schema, such as URL, DOI, or handle"
            )
            return eval.response()

        try:
            r = requests.get(subject_url)
            r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
            eval.success(f"Successfully resolved {subject_url}")
            if r.history:
                eval.info("Request was redirected to " + r.url + ".")
                eval.data["alternative_uris"].append(r.url)

        except Exception as e:
            eval.failure(f"Could not resolve {subject_url}. Getting: {e.args[0]}")

        return eval.response()
