[![Version](https://img.shields.io/pypi/v/fair-test)](https://pypi.org/project/fair-test) [![Python versions](https://img.shields.io/pypi/pyversions/fair-test)](https://pypi.org/project/fair-test)

`fair-test` is a library to build and deploy [FAIR](https://www.go-fair.org/fair-principles/){:target="_blank"} metrics tests APIs, supporting the specifications used by the [FAIRMetrics working group](https://github.com/FAIRMetrics/Metrics){:target="_blank"}, that can be queried to assess if a resource is complying with the [FAIR principles](https://www.go-fair.org/fair-principles/){:target="_blank"} (Findable, Accessible, Interoperable, Reusable).

It aims to enable python developers to easily write, and deploy FAIR metric tests functions that can be queried by various FAIR evaluations services, such as [FAIR enough](https://fair-enough.semanticscience.org/){:target="_blank"} and the [FAIRsharing FAIR Evaluator](https://fairsharing.github.io/FAIR-Evaluator-FrontEnd/){:target="_blank"}.

FAIR metrics tests are evaluations taking a subject URL as input, executing a battery of tests (e.g. checking if machine readable metadata is available at this URL), and returning a score of 0 or 1, with the evaluation logs.

!!! info "Report issues"

    Feel free to create [issues on GitHub](https://github.com/MaastrichtU-IDS/fair-test/issues){:target="_blank"}, if you are facing problems, or would like to see a feature implemented. Pull requests are also welcomed!

## ℹ️ How it works

The user defines custom FAIR metrics tests in python in a specific folder (the `metrics` folder by default), and starts the API. They can then access the API to run the metrics tests on the subject URLs of their choice.

## 📂 Projects using fair-test

Here are some projects using `fair-test` to deploy FAIR test services:

* [https://github.com/MaastrichtU-IDS/fair-enough-metrics](https://github.com/MaastrichtU-IDS/fair-enough-metrics){:target="_blank"}: A generic  FAIR metrics tests service developed at the Institute of Data Science at Maastricht University.
* [https://github.com/LUMC-BioSemantics/RD-FAIRmetric-F4](https://github.com/LUMC-BioSemantics/RD-FAIRmetric-F4){:target="_blank"}: A FAIR metrics tests service for Rare Disease research.

## 🤝 Credits

Library built with [FastAPI](https://fastapi.tiangolo.com/){:target="_blank"}, and [RDFLib](https://github.com/RDFLib/rdflib){:target="_blank"}.

Using the specifications for FAIR evaluation services defined by the [FAIR metrics working group](https://github.com/FAIRMetrics/Metrics){:target="_blank"}.