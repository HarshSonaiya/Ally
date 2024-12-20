from .settings import settings
from elasticsearch import Elasticsearch


# Initialize the Elasticsearch client
def get_es_client():
    return Elasticsearch([settings.ELASTIC_URL])