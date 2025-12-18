from pathlib import Path
from datetime import datetime
from extractors.file_extractors import EXTRACTORS

class OpenSearchIndexer:
    def __init__(self, client, index_name):
        self.client = client
        self.index_name = index_name
        self._ensure_index()

    def _ensure_index(self):
        if self.client.indices.exists(index=self.index_name):
            return
        self.client.indices.create(
            index=self.index_name,
            body={
                "settings": {
                    "analysis": {
                        "tokenizer": {"edge_ngram_tokenizer": {"type": "edge_ngram","min_gram": 2,"max_gram": 20,"token_chars": ["letter", "digit"]}},
                        "analyzer": {"prefix_analyzer": {"type": "custom","tokenizer": "edge_ngram_tokenizer","filter": ["lowercase"]},
                        "standard_lowercase": {"type": "custom","tokenizer": "standard","filter": ["lowercase"]}}}},
                "mappings": {
                    "properties": {
                        "path": {"type": "keyword"},
                        "filename": {"type": "text","analyzer": "prefix_analyzer","search_analyzer": "standard_lowercase"},
                        "filetype": {"type": "keyword"},
                        "modified": {"type": "date"},
                        "size_bytes": {"type": "long"},
                        "content": {"type": "text","analyzer": "prefix_analyzer","search_analyzer": "standard_lowercase"}
                    }
                }
            }
        )

    def index_folder(self, folder: str):
        folder = Path(folder)
        count = 0
        for file in folder.rglob("*"):
            if not file.is_file():
                continue
            extractor = EXTRACTORS.get(file.suffix.lower())
            if not extractor:
                continue
            content = extractor(file)
            if not content:
                continue

            self.client.index(
                index=self.index_name,
                id=str(file.resolve()),
                body={
                    "path": str(file.resolve()),
                    "filename": file.name,
                    "filetype": file.suffix.lower().lstrip("."),
                    "modified": datetime.fromtimestamp(
                        file.stat().st_mtime
                    ).strftime("%Y-%m-%dT%H:%M:%S"),
                    "size_bytes": file.stat().st_size,
                    "content": content
                }
            )
            count += 1
        return count
