from pydantic import BaseModel
from typing import List, Optional

class SearchInput(BaseModel):
    keyword: str
    search_mode: str  # filename or content
    file_types: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    size_from: Optional[int] = None  # KB
    size_to: Optional[int] = None    # KB
    from_: Optional[int] = 0
    size: Optional[int] = 20
