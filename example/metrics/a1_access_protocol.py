import requests
from rdflib.namespace import DCTERMS

from fair_test import FairTest, FairTestEvaluation


class MetricTest(FairTest):
    metric_path = "a1-access-protocol"
    applies_to_principle = "A1"
    title = "Check Access Protocol"
    description = """The access protocol and authorization (if content restricted).
For the protocol , do an HTTP get on the URL to see if it returns a valid document.
Find information about authorization in metadata"""
    author = "https://orcid.org/0000-0002-1501-1082"
    metric_version = "0.1.0"
    test_test = {
        "https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972": 1,
        "https://raw.githubusercontent.com/ejp-rd-vp/resource-metadata-schema/master/data/example-rdf/turtle/patientRegistry.ttl": 1,
        "Wrong entry": 0,
    }

    def evaluate(self, eval: FairTestEvaluation):
        eval.info(f"Access protocol: check resource URI protocol is resolvable for {eval.subject}")
        try:
            r = requests.get(eval.subject)
            r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
            eval.success("Successfully resolved " + eval.subject)
            if r.history:
                eval.info("Request was redirected to " + r.url + ".")
                eval.data["alternative_uris"].append(r.url)

        except Exception as e:
            eval.failure(f"Could not resolve {eval.subject}. Getting: {e.args[0]}")

        eval.info("Authorization: checking for dct:accessRights in metadata")
        g = eval.retrieve_metadata(eval.subject)

        if not isinstance(g, (list, dict)) and len(g) > 1:
            eval.info(
                f"Successfully found and parsed RDF metadata available at {eval.subject}. It contains {str(len(g))} triples"
            )
        else:
            eval.failure(f"No RDF metadata found at the subject URL {eval.subject}")
            return eval.response()

        found_access_rights = False
        access_rights_preds = [DCTERMS.accessRights]
        for pred in access_rights_preds:
            for s, p, accessRights in g.triples((None, pred, None)):
                eval.info(f"Found authorization informations with dcterms:accessRights: {str(accessRights)}")
                # eval.data['accessRights'] = str(accessRights)
                found_access_rights = True

        if found_access_rights:
            eval.success(f"Found dcterms:accessRights in metadata: {str(accessRights)}")
        else:
            eval.warn(
                f"Could not find dcterms:accessRights information in metadata. Make sure your metadata contains informations about access rights using one of those predicates: {', '.join(access_rights_preds)}"
            )

        return eval.response()
