from opensearchpy import OpenSearch
from config.settings import OPENSEARCH_HOST, OPENSEARCH_PORT

def get_client():
    return OpenSearch(
        hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
        http_auth=("admin", "Opensearch@132"),
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False,
    )
