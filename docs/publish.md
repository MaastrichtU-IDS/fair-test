Once your test work as expected it is time to publish and register it, in order to be able to use it in FAIR evaluations services.

You can either publish your new tests directly in our existing FAIR enough metrics API, or publish a new API on your servers.

## 🗞️ First, publish your tests

Multiple are available for publishing your tests:

### ⚡️ Publish your  tests to an existing API

You are welcome to add your tests to the FAIR Enough metrics API. To do so: fork the repository on GitHub, create your metrics tests in the `metrics` folder, and submit a pull request to propose adding your tests to the [FAIR enough metrics API repository](https://github.com/MaastrichtU-IDS/fair-enough-metrics){:target="_blank"}, it will be made available at [https://metrics.api.fair-enough.semanticscience.org](https://metrics.api.fair-enough.semanticscience.org){:target="_blank"}.

!!! success "Persistent URLs"

	This service uses persistent URLs. This means your test will be made permanently available at the URL https://w3id.org/fair-enough/metrics/tests/ + your test path


### 🗄️ Publish a new API on your server

You can also easily deploy a new API on your servers. If you want to start from a project with everything ready to deploy in production, we recommend you to fork the [fair-enough-metrics repository](https://github.com/MaastrichtU-IDS/fair-enough-metrics){:target="_blank"}. Change the configuration in `main.py` and `.env`, and remove the metrics tests to put yours. See the README for more details  on how to deploy with `docker-compose`

### ☁️ Publish a new API to a cloud provider

You can easily publish the docker container running your API using [Google Cloud Run](https://cloud.google.com/run/docs/deploying){:target="_blank"}, or AWS lambda


## 📍 Then, register your tests

Finally, you will need Register your FAIR Metrics Test in a FAIR evaluation service,  such as [FAIR enough](https://fair-enough.semanticscience.org){:target="_blank"}, or the [FAIR evaluator](https://fairsharing.github.io/FAIR-Evaluator-FrontEnd/){:target="_blank"},  to be able to use it as part of FAIR evaluations.

To register your service in FAIR enough:

1. Go to [https://fair-enough.semanticscience.org/metrics](https://fair-enough.semanticscience.org/metrics){:target="_blank"}
3. Provide your publicly available metrics test URL, and click submit.


!!! warning "Use persistent URLs"

	When it has been enabled for the FAIR Test API you want to register, use a persistent URL for the Metrics tests. See [w3id.org](https://w3id.org/){:target="_blank"} to easily create and maintain a persistent URL.

Once your FAIR metrics tests are registered in the FAIR evaluation service, you can create collections that use your tests, and run evaluations with those collections.
