import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import extruct
import idutils
import requests
from pyld import jsonld
from rdflib import ConjunctiveGraph, Dataset, Graph, URIRef

from fair_test.fair_test_logger import FairTestLogger


@dataclass
class MetadataHarvester:
    subject: Optional[str] = None
    alt_urls: list = field(default_factory=list)
    rdf: Optional[Union[Graph, ConjunctiveGraph, Dataset]] = None
    json: Optional[Dict] = None
    data: dict = field(default_factory=dict)
    logs: FairTestLogger = FairTestLogger()

    def get_url(self, id: str) -> str:
        """Return the full URL for a given identifiers (e.g. URL, DOI, handle)"""
        if idutils.is_url(id):
            self.logs.info(f"Validated the resource {id} is a URL")
            return id

        if idutils.is_doi(id):
            self.logs.info(f"Validated the resource {id} is a DOI")
            return idutils.to_url(id, "doi", "https")

        if idutils.is_handle(id):
            self.logs.info(f"Validated the resource {id} is a handle")
            return idutils.to_url(id, "handle", "https")

        # TODO: add INCHI key?
        # inchikey = regexp(/^\w{14}\-\w{10}\-\w$/)
        # return f"https://pubchem.ncbi.nlm.nih.gov/rest/rdf/inchikey/{inchikey}"

        self.logs.warn(f"Could not validate the given resource URI {id} is a URL, DOI, or handle")
        return id

    # TODO: implement metadata extraction with more tools?
    # e.g. Apache Tika for PDF/pptx? or ruby Kellog's Distiller? http://rdf.greggkellogg.net/distiller
    # c.f. https://github.com/FAIRMetrics/Metrics/blob/master/MetricsEvaluatorCode/Ruby/metrictests/fair_metrics_utilities.rb
    def retrieve_metadata(
        self,
        url: str,
        use_harvester: bool = False,
        harvester_url: str = "https://w3id.org/FAIR_Tests/tests/harvester",
    ) -> Any:
        """
        Retrieve metadata from a URL, RDF metadata parsed as a RDFLib Graph in priority.
        Super useful. It tries:
        - Following signposting links (returned in HTTP headers)
        - Extracting JSON-LD embedded in the HTML
        - Asking RDF through content-negociation
        - Can return JSON found as a fallback, if RDF metadata is not found
        You can also use an external harvester API to get the RDF metadata

        Parameters:
            url: URL to retrieve RDF from
            use_harvester: Use an external harvester to retrieve the RDF instead of the built-in python harvester
            harvester_url: URL of the RDF harvester used

        Returns:
            g (Graph): A RDFLib Graph with the RDF found at the given URL
        """
        original_url = url
        url = self.get_url(url)
        if not url:
            self.logs.warn(
                f"The resource {original_url} could not be converted to a valid URL, hence no metadata could be retrieved"
            )
            return []

        if use_harvester == True:
            # Check the harvester response:
            # curl -X POST -d '{"subject": "https://doi.org/10.1594/PANGAEA.908011"}' https://w3id.org/FAIR_Tests/tests/harvester
            try:
                self.logs.info(f"Using Harvester at {harvester_url} to retrieve RDF metadata at {url}")
                res = requests.post(
                    harvester_url,
                    json={"subject": url},
                    timeout=60,
                    allow_redirects=True,
                    headers={"Accept": "application/turtle"},
                )
                return self.parse_rdf(res.text, "text/turtle", log_msg="FAIR evaluator harvester RDF")
            except Exception as e:
                self.logs.warn(
                    f"Could not retrieve metadata from the Harvester service at {harvester_url} for {url}: {e}"
                )

        # https://github.com/FAIRMetrics/Metrics/blob/master/MetricsEvaluatorCode/Ruby/metrictests/fair_metrics_utilities.rb#L355
        html_text = None
        metadata_obj = []
        # Check if URL resolve and if redirection
        # r = requests.head(url)

        try:
            r = requests.get(url)
            r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
            self.logs.info(f"Successfully resolved {url}")
            html_text = r.text
            if r.history:
                # Extract alternative URIs if request redirected
                redirect_url = r.url
                if redirect_url.startswith("https://linkinghub.elsevier.com/retrieve/pii/"):
                    # Special case to handle Elsevier bad redirections to ScienceDirect
                    redirect_url = redirect_url.replace(
                        "https://linkinghub.elsevier.com/retrieve/pii/",
                        "https://www.sciencedirect.com/science/article/pii/",
                    )

                self.data["redirect_url"] = redirect_url
                if url == self.subject and not redirect_url in self.data["alternative_uris"]:
                    self.logs.info(
                        f"Request was redirected to {redirect_url}, adding to the list of alternative URIs for the subject"
                    )
                    self.data["alternative_uris"].append(redirect_url)
                    if r.url.startswith("http://"):
                        self.data["alternative_uris"].append(redirect_url.replace("http://", "https://"))
                    elif r.url.startswith("https://"):
                        self.data["alternative_uris"].append(redirect_url.replace("https://", "http://"))

            # Handle signposting links headers https://signposting.org/FAIR
            if r.links:
                # Follow signposting links, this could create a lot of recursions (to be checked)
                self.logs.info(f"Found Signposting links: {str(r.links)}")
                self.data["signposting_links"] = r.links
                check_rels = ["alternate", "describedby", "meta"]
                # Alternate is used by schema.org
                for rel in check_rels:
                    if rel in r.links.keys():
                        rel_url = r.links[rel]["url"]
                        if not rel_url.startswith("http://") and not rel_url.startswith("https://"):
                            # In some case the rel URL provided is relative to the requested URL
                            if r.url.endswith("/") and rel_url.startswith("/"):
                                rel_url = rel_url[1:]
                            rel_url = r.url + rel_url
                        metadata_obj = self.retrieve_metadata(rel_url)
                        if len(metadata_obj) > 0:
                            return metadata_obj

        except Exception as e:
            self.logs.warn(f"Error resolving the URL {url} : {str(e.args[0])}")

        self.logs.info(
            "Checking for metadata embedded in the HTML page returned by the resource URI " + url + " using extruct"
        )
        # TODO: support client-side JS generated HTML using Selenium https://github.com/vemonet/extruct-selenium
        try:
            if not html_text:
                raise Exception("No HTML text provided")
            extructed = extruct.extract(html_text.encode("utf8"))
            if url == self.subject:
                self.data["extruct"] = extructed
            if len(extructed["json-ld"]) > 0:
                g = self.parse_rdf(extructed["json-ld"], "json-ld", log_msg="HTML embedded JSON-LD RDF")
                if len(g) > 0:
                    self.logs.info(f"Found JSON-LD RDF metadata embedded in the HTML with extruct")
                    return g
                else:
                    metadata_obj = extructed["json-ld"]
            if len(extructed["rdfa"]) > 0:
                g = self.parse_rdf(extructed["rdfa"], "json-ld", log_msg="HTML embedded RDFa")
                if len(g) > 0:
                    self.logs.info(f"Found RDFa metadata embedded in the HTML with extruct")
                    return g
                elif not metadata_obj:
                    metadata_obj = extructed["rdfa"]
            if not metadata_obj and len(extructed["microdata"]) > 0:
                metadata_obj = extructed["microdata"]
            if not metadata_obj and extructed["dublincore"] != [{"namespaces": {}, "elements": [], "terms": []}]:
                # Dublin core always comes as this empty dict if no match
                metadata_obj = extructed["dublincore"]
            # The rest is not extracted because usually give no interesting metadata:
            # opengraph, microformat
        except Exception as e:
            self.logs.info(f"Error when running extruct on {url}. Getting: {str(e.args[0])}")

        # Perform content negociation last because it's the slowest for a lot of URLs like zenodo
        # We need to do direct content negociation to turtle and json
        # because some URLs dont support standard weighted content negociation
        check_mime_types = [
            "text/turtle",
            "application/ld+json",
            "text/turtle, application/turtle, application/x-turtle;q=0.9, application/ld+json;q=0.8, application/rdf+xml, text/n3, text/rdf+n3;q=0.7",
        ]
        for mime_type in check_mime_types:
            try:
                r = requests.get(url, headers={"accept": mime_type})
                r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
                content_type = r.headers["Content-Type"].replace(" ", "").replace(";charset=utf-8", "")
                # If return text/plain we parse as turtle or JSON-LD
                # content_type = content_type.replace('text/plain', 'text/turtle')
                self.logs.info(
                    f"Content-negotiation: found some metadata in {content_type} when asking for {mime_type}"
                )
                try:
                    # If returns JSON
                    self.data["json-ld"] = r.json()
                    if not metadata_obj:
                        metadata_obj = r.json()
                    return self.parse_rdf(r.json(), "json-ld", log_msg="content negotiation JSON-LD RDF")
                except Exception:
                    # If returns RDF as text, such as turtle
                    return self.parse_rdf(r.text, content_type, log_msg="content negotiation RDF")
            except Exception as e:
                self.logs.info(
                    f"Content-negotiation: error with {url} when asking for {mime_type}. Getting {str(e.args[0])}"
                )
                # Error: e.args[0]

        # If nothing found with the built-in metadata harvesting process we try to use the service
        if not metadata_obj or len(metadata_obj) < 1:
            try:
                self.logs.info(
                    f"Nothing found with built-in metadata harvesting process. Using Metadata Harvester service at {harvester_url} to retrieve RDF metadata from {url}"
                )
                res = requests.post(
                    harvester_url,
                    json={"subject": url},
                    timeout=60,
                    allow_redirects=True,
                    headers={"Accept": "application/turtle"},
                )
                res.raise_for_status()
                g = self.parse_rdf(res.text, "text/turtle", log_msg="Metadata harvester service RDF")
                if len(g) > 1:
                    return g
                else:
                    self.logs.warn(f"The Harvester service at {harvester_url} could not find metadata for {url}")
            except Exception as e:
                self.logs.warn(
                    f"Could not retrieve metadata from the Harvester service at {harvester_url} for {url}: {e}"
                )

        return metadata_obj

    def parse_rdf(
        self,
        rdf_data: Any,
        mime_type: Optional[str] = None,
        log_msg: Optional[str] = "",
    ) -> Any:
        """
        Parse any string or JSON-like object to a RDFLib Graph

        Parameters:
            rdf_data (str|object): Text or object to convert to RDF
            mime_type: Mime type of the data to convert
            log_msg: Text to use when logging about the parsing process (help debugging)

        Returns:
            g (Graph): A RDFLib Graph
        """
        # https://rdflib.readthedocs.io/en/stable/plugin_parsers.html
        parse_formats = ["turtle", "json-ld", "xml", "ntriples", "nquads", "trig", "n3"]

        if type(rdf_data) == dict:
            rdf_data = [rdf_data]
        if type(rdf_data) == list:
            for rdf_entry in rdf_data:
                try:
                    # Dirty hack to fix RDFLib that is not able to parse JSON-LD schema.org (https://github.com/schemaorg/schemaorg/issues/2578)
                    if "@context" in rdf_entry:
                        if isinstance(rdf_entry["@context"], str):
                            if rdf_entry["@context"].startswith("http://schema.org") or rdf_entry[
                                "@context"
                            ].startswith("https://schema.org"):
                                rdf_entry["@context"] = "https://schema.org/docs/jsonldcontext.json"
                        if isinstance(rdf_entry["@context"], list):
                            for i, cont in enumerate(rdf_entry["@context"]):
                                if isinstance(cont, str):
                                    rdf_entry["@context"][i] = "https://schema.org/docs/jsonldcontext.json"
                except:
                    pass
            # RDFLib JSON-LD had issue with encoding: https://github.com/RDFLib/rdflib/issues/1416
            rdf_data = jsonld.expand(rdf_data)
            rdf_data = json.dumps(rdf_data)
            parse_formats = ["json-ld"]

        else:
            # Try to guess the format to parse from mime type
            if mime_type:
                mime_type = mime_type.split(";")[0]
                if "turtle" in mime_type:
                    parse_formats = ["turtle"]
                elif "xml" in mime_type:
                    parse_formats = ["xml"]
                elif "ntriples" in mime_type:
                    parse_formats = ["ntriples"]
                elif "nquads" in mime_type:
                    parse_formats = ["nquads"]
                elif "trig" in mime_type:
                    parse_formats = ["trig"]
                # elif mime_type.startswith('text/html'):
                #     parse_formats = []

        g = ConjunctiveGraph()
        # Remove some auto-generated triples about the HTML content
        remove_preds = ["http://www.w3.org/1999/xhtml/vocab#role"]
        for rdf_format in parse_formats:
            try:
                g = ConjunctiveGraph()
                g.parse(data=rdf_data, format=rdf_format)

                for rm_pred in remove_preds:
                    g.remove((None, URIRef(rm_pred), None))

                self.logs.info(
                    f"Successfully parsed {mime_type} RDF from {log_msg} with parser {rdf_format}, containing {str(len(g))} triples"
                )
                return g
            except Exception as e:
                self.logs.info(
                    f"Could not parse {mime_type} metadata from {log_msg} with parser {rdf_format}. Getting error: {str(e)}"
                )
        return g
        # return None

    @property
    def comment(self) -> List[str]:
        return self.logs.logs

    @property
    def asdict(self) -> Dict[str, Any]:
        dic = {
            "subject": self.subject,
            "json": self.json,
            "comment": self.comment,
        }
        if self.rdf:
            dic["rdf"] = json.load(self.rdf.serialize(format="json-ld"))
        return dic

    # def __post_init__(self):
    #     self.retrieve_metadata(self.subject)
