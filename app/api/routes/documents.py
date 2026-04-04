from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.document import Document
from app.schemas.document import DocumentCreate,DocumentResponse

router = APIRouter(prefix="/documents")


@router.post("/", status_code=201,response_model=DocumentResponse)
def create_document(document_create: DocumentCreate, db: Session = Depends(get_db)):
    document = Document(title=document_create.title, content=document_create.content)
    db.add(document)
    db.commit()
    db.refresh(document)

    return document
