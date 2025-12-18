from fastapi import FastAPI
from routes.indexing_routes import router as indexing_router
from routes.search_routes import router as search_router
from config.settings import OPENSEARCH_INDEX

app = FastAPI(title="OpenSearch File Search API")

app.include_router(indexing_router, prefix="/api")
app.include_router(search_router, prefix="/api")

@app.get("/")
def root():
    return {
        "status": "success",
        "message": "API running",
        "endpoints": ["/api/index-folder", "/api/search"]
    }

print("Loaded index:", OPENSEARCH_INDEX)


# To run this application, use the command:

# Open cmd - cd C:\Users\Admin\Downloads\opensearch-3.3.2-windows-x64\opensearch-3.3.2
# add bin\opensearch.bat

# then run:
# uvicorn main:app --reload