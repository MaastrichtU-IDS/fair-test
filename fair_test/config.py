from pydantic import BaseSettings


# Settings of the API
class Settings(BaseSettings):
    HOST: str = "metrics.api.fair-enough.semanticscience.org"
    BASE_URI: str = "https://metrics.api.fair-enough.semanticscience.org"
    # HOST: str = "w3id.org/fair-enough/metrics"
    # BASE_URI: str = "https://w3id.org/fair-enough/metrics"
    CONTACT_URL: str = 'https://github.com/MaastrichtU-IDS/fair-enough-metrics'
    CONTACT_NAME: str = 'Vincent Emonet'
    CONTACT_EMAIL: str = 'vincent.emonet@gmail.com'
    CONTACT_ORCID: str = '0000-0002-1501-1082'
    ORG_NAME: str = 'Institute of Data Science at Maastricht University'
    DEFAULT_SUBJECT: str = 'https://doi.org/10.1594/PANGAEA.908011'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
