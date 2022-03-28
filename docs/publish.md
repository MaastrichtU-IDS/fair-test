Once your test work as expected it is time to publish and register it, in order to be able to use it in FAIR evaluations services.

You can either publish your new tests directly in our existing FAIR enough metrics API, or publish a new API on your servers.

## ⚡️ Publish your  tests to an existing API

You are welcome to add your tests to the FAIR Enough metrics API. To do so: fork the repository on GitHub, create your metrics tests in the `metrics` folder, and submit a pull request to propose adding your tests to the [FAIR enough metrics API repository](https://github.com/MaastrichtU-IDS/fair-enough-metrics){:target="_blank"}, it will be made available at [https://metrics.api.fair-enough.semanticscience.org](https://metrics.api.fair-enough.semanticscience.org){:target="_blank"}.

!!! info "Persistent URLs"

	This service uses persistent URLs. This means your test will be made permanently available at the URL https://metrics.api.fair-enough.semanticscience.org/tests/ + your test path


## 🗄️ Or publish a new API on your server

You can also easily deploy a new API on your servers. If you want to start from a project with everything ready to deploy in production, we recommend you to fork the [fair-enough-metrics repository](https://github.com/MaastrichtU-IDS/fair-enough-metrics){:target="_blank"}. Change the configuration in `main.py` and `.env`, and remove the metrics tests to put yours. See the README for more details  on how to deploy with `docker-compose`


## 📍 Register

Register your FAIR Metrics Test in a FAIR evaluation service,  such as [FAIR enough](https://fair-enough.semanticscience.org), or the [FAIR evaluator](https://fairsharing.github.io/FAIR-Evaluator-FrontEnd/).

To register your service in FAIR enough:

1. Go to [https://fair-enough.semanticscience.org/metrics](https://fair-enough.semanticscience.org/metrics){:target="_blank"}
3. Provide your publicly available metrics test URL, and click submit.


!!! warning "Use persistent URLs"

	When it has been enabled for the FAIR Test API, use your Metrics test persistent URL.