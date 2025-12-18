from opensearchpy import OpenSearch
from config.settings import OPENSEARCH_HOST, OPENSEARCH_PORT

def get_client():
    return OpenSearch(
        hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
        use_ssl=False,
        verify_certs=False
    )
