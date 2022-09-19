import io
import re

import requests

from fair_test import FairTest, FairTestEvaluation


class MetricTest(FairTest):
    metric_path = "i2-fair-vocabularies"
    applies_to_principle = "I2"
    title = "Metadata uses FAIR Vocabularies"
    description = """The metadata values and qualified relations should
themselves be FAIR, for example, terms from open, community-accepted
vocabularies published in an appropriate knowledge-exchange format.
Resolve IRIs, check FAIRness of the returned documents."""
    author = "https://orcid.org/0000-0002-1501-1082"
    metric_version = "0.1.0"
    test_test = {
        "https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972": 1,
        "https://doi.org/10.1594/PANGAEA.908011": 1,
        "http://example.com": 0,
    }

    def evaluate(self, eval: FairTestEvaluation):
        # LOV docs: https://lov.linkeddata.es/dataset/lov/api
        lov_api = "https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/list"
        lod_cloudnet = "https://lod-cloud.net/lod-data.json"

        # g = eval.retrieve_metadata(eval.subject)
        g = eval.retrieve_metadata(eval.subject, use_harvester=True)
        if len(g) == 0:
            eval.failure("No RDF found at the subject URL provided.")
            return eval.response()
        else:
            eval.info(f"RDF metadata containing {len(g)} triples found at the subject URL provided.")

        # eval.info('Checking RDF metadata vocabularies')
        rdflib_ns = [n for n in g.namespace_manager.namespaces()]
        # print('Extracted with RDFLib: ', rdflib_ns)
        # rdflib_ns = [n for n in g.namespaces()]
        # print(rdflib_ns)
        # Checkout the prefixes/namespaces
        # for ns_prefix, namespace in g.namespaces():
        #     print(ns_prefix, ' => ', namespace)

        # Extract namespace manually because RDFLib can't do it
        extracted_ns = []
        for row in io.StringIO(g.serialize(format="turtle")):
            if row.startswith("@prefix"):
                pattern = re.compile("^.*<(.*?)>")
                ns = pattern.search(row).group(1)
                extracted_ns.append(ns)
        # print('Extracted manually: ', extracted_ns)

        validated_ns = set()
        tested_ns = set()
        ignore_ns = []
        eval.info("Check if used vocabularies in Linked Open Vocabularies: " + lov_api)
        lov_list = requests.get(lov_api).json()
        for vocab in lov_list:
            if vocab["nsp"] in ignore_ns:
                continue

            # Check for manually extracted ns
            for ns in extracted_ns:
                tested_ns.add(ns)
                if vocab["nsp"].startswith(ns):
                    validated_ns.add(ns)

            # Check for RDFLib extracted ns
            for index, tuple in rdflib_ns:
                tested_ns.add(tuple[1])
                # if vocab['nsp'].startswith(tuple[1]):
                if tuple[1].startswith(vocab["nsp"]):
                    validated_ns.add(tuple[1])

        if len(validated_ns) > 0:
            eval.success(
                "Found vocabularies used by the resource metadata in the Linked Open Vocabularies: "
                + ", ".join(validated_ns)
            )
        else:
            eval.failure(
                "Could not find vocabularies used by the resource metadata in the Linked Open Vocabularies: "
                + ", ".join(tested_ns)
            )

        # eval.info('Check if used vocabularies in the LOD cloud: ' + lod_cloudnet)
        # https://github.com/vemonet/fuji/blob/master/fuji_server/helper/preprocessor.py#L368

        return eval.response()
