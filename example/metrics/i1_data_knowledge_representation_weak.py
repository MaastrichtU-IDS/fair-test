import requests
import yaml

from fair_test import FairTest, FairTestEvaluation


class MetricTest(FairTest):
    metric_path = "i1-data-knowledge-representation-weak"
    applies_to_principle = "I1"
    title = "Data uses a formal knowledge representation language (weak)"
    description = """Maturity Indicator to test if the data uses a formal language broadly applicable for knowledge representation.
This particular test takes a broad view of what defines a 'knowledge representation language'; in this evaluation, anything that can be represented as structured data will be accepted"""
    author = "https://orcid.org/0000-0002-1501-1082"
    metric_version = "0.1.0"
    test_test = {
        "https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972": 1,
        "https://doi.org/10.1594/PANGAEA.908011": 0,
    }

    def evaluate(self, eval: FairTestEvaluation):
        g = eval.retrieve_metadata(eval.subject)
        if len(g) > 1:
            eval.info(f"Successfully found and parsed RDF metadata. It contains {str(len(g))} triples")

        subject_uri = eval.extract_metadata_subject(g, eval.data["alternative_uris"])
        # Retrieve URI of the data in the RDF metadata
        data_res = eval.extract_data_subject(g, subject_uri)
        if len(data_res) < 1:
            eval.failure("Could not find data URI in the metadata.")
        else:
            eval.data["data_uri"] = data_res

        # Check if structured data can be found at the data URI
        for value in data_res:
            eval.info(f"Found data URI: {value}. Try retrieving RDF")
            data_g = eval.retrieve_metadata(value)
            if len(data_g) > 1:
                eval.info(f"Successfully retrieved RDF for the data URI: {value}. It contains {str(len(g))} triples")
                eval.success(f"Successfully found and parsed RDF data for {value}")

            else:
                eval.warn(f"No RDF data found for {value}, searching for JSON")
                try:
                    r = requests.get(value, headers={"accept": "application/json"})
                    metadata = r.json()
                    eval.data["metadata_json"] = metadata
                    eval.success(f"Successfully found and parsed JSON data for {value}")
                except:
                    eval.warn(f"No JSON metadata found for {value}, searching for YAML")
                    try:
                        r = requests.get(value, headers={"accept": "text/yaml"})
                        metadata = yaml.load(r.text, Loader=yaml.FullLoader)
                        eval.data["metadata_yaml"] = metadata
                        eval.success(f"Successfully found and parsed YAML data for {value}")
                    except:
                        eval.failure(f"No YAML metadata found for {value}")

        return eval.response()
