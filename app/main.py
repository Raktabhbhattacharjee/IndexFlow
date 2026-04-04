from app.db.base import Base
from app.db.session import engine
from app.models import document, search_index
from app.api.routes import documents,search
from fastapi import FastAPI


app = FastAPI()
app.include_router(documents.router)
app.include_router(search.router)
Base.metadata.create_all(bind=engine)