[![Version](https://img.shields.io/pypi/v/fair-test)](https://pypi.org/project/fair-test) [![Python versions](https://img.shields.io/pypi/pyversions/fair-test)](https://pypi.org/project/fair-test)

`fair-test` is a library to build and deploy [FAIR](https://www.go-fair.org/fair-principles/){:target="_blank"} metrics tests APIs supporting the specifications used by the [FAIRMetrics working group](https://github.com/FAIRMetrics/Metrics){:target="_blank"}. 

It aims to enable python developers to easily write, and deploy FAIR metric tests functions that can be queried by various FAIR evaluations services, such as [FAIR enough](https://fair-enough.semanticscience.org/){:target="_blank"} and the [FAIRsharing FAIR Evaluator](https://fairsharing.github.io/FAIR-Evaluator-FrontEnd/){:target="_blank"}

FAIR metrics tests are evaluations taking a subject URL as input, executing a battery of tests (e.g. checking if machine readable metadata is available at this URL), and returning a score of 0 or 1, with the evaluation logs.

!!! info "Report issues"

    Feel free to create an [issue](https://github.com/MaastrichtU-IDS/fair-test/issues){:target="_blank"} on GitHub, or send a pull request if you are facing issues or would like to see a feature implemented.

## ℹ️ How it works

The user defines and registers custom FAIR metrics tests in separated files in a specific folder (the `metrics` folder by default), and start the API.

Built with [FastAPI](https://fastapi.tiangolo.com/){:target="_blank"}, and [RDFLib](https://github.com/RDFLib/rdflib){:target="_blank"}. Tested for Python 3.7, 3.8 and 3.9


## 📂 Projects using fair-test

Here are some projects using `fair-test` to deploy FAIR test services:

* [https://github.com/MaastrichtU-IDS/fair-enough-metrics](https://github.com/MaastrichtU-IDS/fair-enough-metrics){:target="_blank"}: A generic  FAIR metrics tests service developed at the Institute of Data Science at Maastricht University.
* [https://github.com/LUMC-BioSemantics/RD-FAIRmetric-F4](https://github.com/LUMC-BioSemantics/RD-FAIRmetric-F4){:target="_blank"}: A FAIR metrics tests service for Rare Disease research.
