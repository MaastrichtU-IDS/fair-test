import requests
import yaml

from fair_test import FairTest, FairTestEvaluation


class MetricTest(FairTest):
    metric_path = "i1-metadata-knowledge-representation-weak"
    applies_to_principle = "I1"
    title = "Metadata uses a formal knowledge representation language (weak)"
    description = """Maturity Indicator to test if the metadata uses a formal language broadly applicable for knowledge representation.
This particular test takes a broad view of what defines a 'knowledge representation language'; in this evaluation, anything that can be represented as structured data will be accepted"""
    author = "https://orcid.org/0000-0002-1501-1082"
    metric_version = "0.1.0"
    test_test = {
        "https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972": 1,
        "https://doi.org/10.1594/PANGAEA.908011": 1,
        "https://w3id.org/FAIR_Tests/tests/gen2_structured_metadata": 1,
        "http://example.com": 0,
    }

    def evaluate(self, eval: FairTestEvaluation):
        # https://github.com/vemonet/fuji/blob/master/fuji_server/helper/preprocessor.py#L190
        g = eval.retrieve_metadata(eval.subject)
        if len(g) > 1:
            eval.success(
                "Successfully parsed the RDF metadata retrieved with content negotiation. It contains "
                + str(len(g))
                + " triples"
            )
        else:
            eval.warn("No RDF metadata found, searching for JSON")
            try:
                r_json = requests.get(eval.subject, headers={"accept": "application/json"})
                metadata = r_json.json()
                eval.data["metadata_json"] = metadata
                eval.success("Successfully found and parsed JSON metadata")
            except:
                eval.warn("No JSON metadata found, searching for YAML")
                try:
                    r_yaml = requests.get(eval.subject, headers={"accept": "text/yaml"})
                    metadata = yaml.load(str(r_yaml.text), Loader=yaml.FullLoader)
                    eval.data["metadata_yaml"] = metadata
                    eval.success("Successfully found and parsed YAML metadata")
                except Exception:
                    eval.failure("No YAML metadata found")

        return eval.response()
