from fair_test import FairTestAPI, settings


app = FairTestAPI(
    title='FAIR enough metrics tests API',
    metrics_folder_path='metrics',
    
    description="""FAIR Metrics tests API for resources related to research. Follows the specifications described by the [FAIRMetrics](https://github.com/FAIRMetrics/Metrics) working group.
[![Test Metrics](https://github.com/MaastrichtU-IDS/fair-enough-metrics/actions/workflows/test.yml/badge.svg)](https://github.com/MaastrichtU-IDS/fair-enough-metrics/actions/workflows/test.yml)
[Source code](https://github.com/MaastrichtU-IDS/fair-enough-metrics)    
""",
    license_info = {
        "name": "MIT license",
        "url": "https://opensource.org/licenses/MIT"
    },
    contact = {
        "name": settings.CONTACT_NAME,
        "email": settings.CONTACT_EMAIL,
        "url": settings.CONTACT_URL,
        "x-id": settings.CONTACT_ORCID,
    },
)
