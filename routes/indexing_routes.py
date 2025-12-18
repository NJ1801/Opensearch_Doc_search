from fastapi import APIRouter, HTTPException
from models.indexing_models import FolderInput
from opensearch_client.client import get_client
from opensearch_client.indexer import OpenSearchIndexer
from config.settings import OPENSEARCH_INDEX
from utils.response import success_response

router = APIRouter()

@router.post("/index-folder")
def index_folder(payload: FolderInput):
    client = get_client()
    indexer = OpenSearchIndexer(client, OPENSEARCH_INDEX)
    count = indexer.index_folder(payload.folder)
    return success_response("Folder indexed", {"files_indexed": count})
