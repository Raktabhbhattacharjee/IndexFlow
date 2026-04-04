"""
IndexFlow Indexing Worker (Phase 1)

This module is responsible for the asynchronous processing path.
It periodically checks for documents with 'pending' status and transforms
them into a searchable representation.

Key Responsibilities:
- Poll the documents table for pending documents
- Apply Phase 1 indexing logic (lowercase + remove punctuation)
- Write the cleaned text into the search_index table
- Update the document status to 'indexed'

Important Boundary:
    This worker MUST NOT contain any API logic or HTTP handling.
    It only reads from 'documents' and writes to 'search_index'.
"""

import time
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.document import Document
from app.models.search_index import SearchIndex
from app.core.text import clean_text_for_search



def process_pending_documents(db: Session) -> None:
    """
    Fetch all pending documents and index them in bulk.

    Solves the N+1 problem by:
        1. Fetching all pending documents in one query
        2. Fetching all related search_index rows in one query
        3. Building a lookup map to avoid per-document queries inside the loop

    Args:
        db: SQLAlchemy session
    """
    stmt = select(Document).where(Document.indexing_status == "pending")
    pending_docs = db.execute(stmt).scalars().all()

    if not pending_docs:
        return

    print(f"[Indexer] Found {len(pending_docs)} pending document(s)")

    # Fetch all existing search_index rows for pending documents in one query
    doc_ids = [doc.id for doc in pending_docs]
    stmt = select(SearchIndex).where(SearchIndex.document_id.in_(doc_ids))
    existing_indexes = db.execute(stmt).scalars().all()

    # Build lookup map — document_id → SearchIndex row
    index_map = {si.document_id: si for si in existing_indexes}

    for doc in pending_docs:
        try:
            print(f"[Indexer] Processing document ID: {doc.id} | Title: {doc.title[:60]}")

            searchable_text = clean_text_for_search(doc.title, doc.content)
            current_time = datetime.now(timezone.utc)
            search_index = index_map.get(doc.id)

            if search_index:
                # Update existing search_index row
                search_index.searchable_text = searchable_text
                search_index.last_indexed_at = current_time
            else:
                # Create new search_index row
                db.add(SearchIndex(
                    document_id=doc.id,
                    searchable_text=searchable_text,
                    last_indexed_at=current_time
                ))

            doc.indexing_status = "indexed"
            doc.updated_at = current_time

            print(f"[Indexer] Successfully indexed document {doc.id}")

        except Exception as e:
            print(f"[Indexer] Failed to process document {doc.id}: {e}")
            doc.indexing_status = "failed"

    try:
        db.commit()
    except Exception as e:
        print(f"[Indexer] Failed to commit batch: {e}")
        db.rollback()


def run_indexer() -> None:
    """
    Main worker loop.

    Runs indefinitely, polling the database every 5 seconds.
    Each cycle opens a fresh DB session, processes all pending
    documents, then closes the session.

    This is a simple polling approach suitable for Phase 1.
    A proper queue will replace this in later phases.
    """
    print("[Indexer] Starting IndexFlow worker...")
    print("[Indexer] Polling for pending documents every 5 seconds...")

    while True:
        db: Session = SessionLocal()
        try:
            process_pending_documents(db)
        except Exception as e:
            print(f"[Indexer] Unexpected error in worker cycle: {e}")
            db.rollback()
        finally:
            db.close()

        time.sleep(5)


if __name__ == "__main__":
    run_indexer()