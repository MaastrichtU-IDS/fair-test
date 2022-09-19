from rdflib import URIRef
from rdflib.namespace import DC, DCTERMS, RDFS

from fair_test import FairTest, FairTestEvaluation


class MetricTest(FairTest):
    metric_path = "f3-id-in-metadata"
    applies_to_principle = "F3"
    title = "Resource Identifier is in Metadata"
    description = """Whether the metadata document contains the globally unique and persistent identifier for the digital resource.
Parse the metadata to search for the given digital resource GUID.
If found, retrieve informations about this resource (title, description, date created, etc)"""
    author = "https://orcid.org/0000-0002-1501-1082"
    metric_version = "0.1.0"
    test_test = {
        "https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/c5414323-eab1-483f-a883-77951f246972": 1,
        "https://doi.org/10.1594/PANGAEA.908011": 1,
        "https://w3id.org/AmIFAIR": 1,
        "http://example.com": 0,
    }

    def evaluate(self, eval: FairTestEvaluation):

        g = eval.retrieve_metadata(eval.subject)
        if len(g) == 0:
            eval.failure("No RDF found at the subject URL provided.")
            return eval.response()
        else:
            eval.info(f"RDF metadata containing {len(g)} triples found at the subject URL provided.")

        # FDP specs: https://github.com/FAIRDataTeam/FAIRDataPoint-Spec/blob/master/spec.md
        # Stats for KG: https://www.w3.org/TR/hcls-dataset

        eval.info(
            f"Checking RDF metadata to find links to all the alternative identifiers: <{'>, <'.join(eval.data['alternative_uris'])}>"
        )
        subject_uri = eval.extract_metadata_subject(g, eval.data["alternative_uris"])

        if subject_uri:
            if "properties" in eval.data["identifier_in_metadata"].keys():
                eval.info(
                    "Found properties/links for the subject URI in the metadata: "
                    + ", ".join(list(eval.data["identifier_in_metadata"]["properties"].keys()))
                )
            if "linked_to" in eval.data["identifier_in_metadata"].keys():
                eval.info(
                    "Found properties/links for the subject URI in the metadata: "
                    + ", ".join(list(eval.data["identifier_in_metadata"]["linked_to"].keys()))
                )
            eval.success(f"Found the subject identifier in the metadata: {str(subject_uri)}")

            # Try to extract some metadata from the parsed RDF
            title_preds = [
                DC.title,
                DCTERMS.title,
                RDFS.label,
                URIRef("http://schema.org/name"),
                URIRef("https://schema.org/name"),
            ]
            # titles = eval.extract_prop(g, title_preds, eval.data['alternative_uris'])
            titles = eval.extract_prop(g, title_preds, subject_uri)
            if len(titles) > 0:
                eval.log(f"Found titles: {' ,'.join(titles)}")
                eval.data["title"] = titles

            description_preds = [
                DCTERMS.description,
                URIRef("http://schema.org/description"),
                URIRef("https://schema.org/description"),
            ]
            descriptions = eval.extract_prop(g, description_preds, subject_uri)
            if len(descriptions) > 0:
                eval.log(f"Found descriptions: {' ,'.join(descriptions)}")
                eval.data["description"] = descriptions

            date_created_preds = [
                DCTERMS.created,
                URIRef("http://schema.org/dateCreated"),
                URIRef("http://schema.org/datePublished"),
            ]
            dates = eval.extract_prop(g, date_created_preds, subject_uri)
            if len(dates) > 0:
                eval.log(f"Found created date: {' ,'.join(dates)}")
                eval.data["created"] = dates

        else:
            eval.failure(f"Could not find links to the subject URI {str(subject_uri)} in the RDF metadata")

        return eval.response()
