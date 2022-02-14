from fair_test import FairTestAPI, settings


app = FairTestAPI(
    title='FAIR Metrics tests API',
    metrics_folder_path='metrics',
    
    description="""FAIR Metrics tests API for resources related to research. Follows the specifications described by the [FAIRMetrics](https://github.com/FAIRMetrics/Metrics) working group.""",
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
