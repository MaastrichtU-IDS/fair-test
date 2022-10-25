[![Version](https://img.shields.io/pypi/v/fair-test)](https://pypi.org/project/fair-test) [![Python versions](https://img.shields.io/pypi/pyversions/fair-test)](https://pypi.org/project/fair-test) [![MIT license](https://img.shields.io/pypi/l/fair-test)](https://github.com/MaastrichtU-IDS/fair-test/blob/main/LICENSE)

`fair-test` is a Python library to build and deploy [FAIR](https://www.go-fair.org/fair-principles/){:target="_blank"} metrics tests APIs, supporting the specifications used by the [FAIRMetrics working group](https://github.com/FAIRMetrics/Metrics){:target="_blank"}. Those APIs can then be queried to assess if a resource is complying with the [FAIR principles](https://www.go-fair.org/fair-principles/){:target="_blank"} (Findable, Accessible, Interoperable, Reusable).

It aims to enable Python developers to easily write, and deploy FAIR metric tests functions that can be queried by various FAIR evaluations services, such as [FAIR enough](https://fair-enough.semanticscience.org/){:target="_blank"} and the [FAIRsharing FAIR Evaluator](https://fairsharing.github.io/FAIR-Evaluator-FrontEnd/){:target="_blank"}.

FAIR metrics tests are evaluations taking a subject URL as input, executing a battery of tests (e.g. checking if machine readable metadata is available at this URL), and returning a score of 0 or 1, with the evaluation logs.

## ℹ️ How it works

You define FAIR metric tests using custom python objects in separate files in a specific folder. The objects will guide you to provide all required metadata for your test as attributes, and implement the test evaluation logic as a function. The library also provides additional helper functions for common tasks, such as retrieving metadata from a URL, or testing a metric test.

These tests can then be deployed as a web API, and registered in central FAIR evaluation service supporting the FAIR metrics working group framework, such as [FAIR enough](https://fair-enough.semanticscience.org) or the [FAIR evaluator](https://fairsharing.github.io/FAIR-Evaluator-FrontEnd/). Finally, users of the evaluation services will be able to group the registered metrics tests in collections used to assess the quality of publicly available digital objects.

!!! help "Report issues"

    Feel free to create [issues on GitHub](https://github.com/MaastrichtU-IDS/fair-test/issues){:target="_blank"}, if you are facing problems, have a question, or would like to see a feature implemented. Pull requests are welcome!

## 🗃️ Projects using fair-test

Here are some projects using `fair-test` to deploy FAIR test services:

* [https://github.com/MaastrichtU-IDS/fair-enough-metrics](https://github.com/MaastrichtU-IDS/fair-enough-metrics){:target="_blank"}: A generic  FAIR metrics tests service developed at the Institute of Data Science at Maastricht University.
* [https://github.com/LUMC-BioSemantics/RD-FAIRmetric-F4](https://github.com/LUMC-BioSemantics/RD-FAIRmetric-F4){:target="_blank"}: A FAIR metrics tests service for Rare Disease research.

## 🤝 Credits

Thanks to the people behind the FAIR evaluation services [FAIR evaluator](https://fairsharing.github.io/FAIR-Evaluator-FrontEnd/#!/), [F-UJI](https://f-uji.net/), and [FAIR Checker](https://fair-checker.france-bioinformatique.fr/), for the various inspirations and ideas.

Thanks to the [FAIR metrics working group](https://github.com/FAIRMetrics/Metrics){:target="_blank"} for the specifications for FAIR evaluation services they defined.

Library built with [FastAPI](https://fastapi.tiangolo.com/){:target="_blank"}, and [RDFLib](https://github.com/RDFLib/rdflib){:target="_blank"}.
