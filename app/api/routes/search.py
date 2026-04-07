from fastapi import APIRouter, Depends,Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.text import clean_text_for_search,tokenize
from app.models.search_index import SearchIndex
from app.models.document import Document
from sqlalchemy import select,or_
from app.schemas.document import DocumentCreate, DocumentResponse
from typing import List
from app.core.ranking import rank_documents

router = APIRouter(prefix="/documents")


@router.get("/search",response_model=List[DocumentResponse])
def search_documents(q: str =Query(min_length=1), db: Session = Depends(get_db)):
    #     """
    #     """
    # Search for documents matching the given query.

    # Steps:
    #     1. Tokenize the raw query into individual keywords
    #     2. Build one LIKE condition per token, combined with OR
    #     3. Find matching rows in search_index
    #     4. Fetch full documents by matched ids
    #     5. Rank results by total term frequency across all tokens"""
        

    tokens = tokenize(q)
    conditions = [SearchIndex.searchable_text.contains(token) for token in tokens]
    search_query = select(SearchIndex).where(or_(*conditions))
    matched_indexes = db.execute(search_query).scalars().all()

    if not matched_indexes:
        return []

    searchable_texts = {index.document_id: index.searchable_text for index in matched_indexes}
    matched_doc_ids = [index.document_id for index in matched_indexes]
    
    fetch_query = select(Document).where(Document.id.in_(matched_doc_ids))
    matched_documents = db.execute(fetch_query).scalars().all()

    return rank_documents(matched_documents, searchable_texts, tokens)

    