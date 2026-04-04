from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.text import clean_text_for_search
from app.models.search_index import SearchIndex
from app.models.document import Document
from sqlalchemy import select


router = APIRouter(prefix="/documents")


@router.get("/search")
def search_documents(q: str, db: Session = Depends(get_db)):
    """
    Search for documents matching the given query.

    Steps:
        1. Clean the query using Phase 1 indexing logic
        2. Find matching rows in search_index using keyword matching
        3. Extract document ids from matches
        4. Fetch and return the full documents

    Args:
        q: Raw search query from the client
        db: Database session

    Note:
        This endpoint queries search_index only — never documents directly.
        That is a core system invariant.
    """
    cleaned_query = clean_text_for_search(q, "")

    search_query = select(SearchIndex).where(
        SearchIndex.searchable_text.contains(cleaned_query)
    )
    matched_indexes = db.execute(search_query).scalars().all()

    if not matched_indexes:
        return []

    matched_doc_ids = [index.document_id for index in matched_indexes]

    fetch_query = select(Document).where(Document.id.in_(matched_doc_ids))
    matched_documents = db.execute(fetch_query).scalars().all()

    return matched_documents
