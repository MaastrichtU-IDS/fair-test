import requests

from fair_test import FairTest, FairTestEvaluation


class MetricTest(FairTest):
    metric_path = "r1-accessible-license"
    applies_to_principle = "R1"
    title = "Check accessible Usage License"
    description = """The existence of a license document, for BOTH (independently) the data and its associated metadata, and the ability to retrieve those documents
Resolve the licenses IRI"""
    author = "https://orcid.org/0000-0002-1501-1082"
    metric_version = "0.1.0"
    test_test = {
        "https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972": 1,
        "https://doi.org/10.1594/PANGAEA.908011": 1,
        "https://w3id.org/AmIFAIR": 1,
        "http://example.com": 0,
    }

    def evaluate(self, eval: FairTestEvaluation):
        # found_license = False
        # Issue with extracting license from some URIs, such as https://www.uniprot.org/uniprot/P51587
        # Getting a URI that is not really the license as output

        # g = eval.retrieve_metadata(eval.subject)
        g = eval.retrieve_metadata(
            eval.subject,
            use_harvester=True,
            harvester_url="http://wrong-url-for-testing",
        )

        if len(g) == 0:
            eval.failure("No RDF found at the subject URL provided.")
            return eval.response()
        else:
            eval.info(f"RDF metadata containing {len(g)} triples found at the subject URL provided.")

        eval.info(
            f"Checking RDF metadata to find links to all the alternative identifiers: <{'>, <'.join(eval.data['alternative_uris'])}>"
        )
        subject_uri = eval.extract_metadata_subject(g, eval.data["alternative_uris"])

        # TODO: check DataCite too?
        license_preds = [
            "http://purl.org/dc/terms/license",
            "https://schema.org/license",
            "http://www.w3.org/1999/xhtml/vocab#license",
        ]

        eval.info(f"Checking for license in RDF metadata using predicates: {str(license_preds)}")
        licenses = eval.extract_prop(g, license_preds, subject_uri)
        if len(licenses) > 0:
            eval.success(f"Found licenses: {' ,'.join(licenses)}")
            eval.data["license"] = licenses
        else:
            eval.failure(
                f"Could not find a license in the metadata. Searched for the following predicates: {str(license_preds)}"
            )

        if "license" in eval.data.keys():
            for license_found in eval.data["license"]:
                eval.info(
                    f"Check if license {eval.data['license']} is approved by the Open Source Initiative, in the SPDX licenses list"
                )
                # https://github.com/vemonet/fuji/blob/master/fuji_server/helper/preprocessor.py#L229
                spdx_licenses_url = "https://raw.github.com/spdx/license-list-data/master/json/licenses.json"
                spdx_licenses = requests.get(spdx_licenses_url).json()["licenses"]
                for open_license in spdx_licenses:
                    if license_found in open_license["seeAlso"]:
                        if open_license["isOsiApproved"] == True:
                            eval.bonus(
                                "License approved by the Open Source Initiative (" + str(eval.data["license"]) + ")"
                            )

        return eval.response()
