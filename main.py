from fastapi import FastAPI

from app.database import Base, engine
from app.routers import produtos

app = FastAPI(
    title="API de Produtos — E-commerce",
    description="Gerenciamento de catálogo com FastAPI + SQLAlchemy + PostgreSQL.",
    version="2.0.0",
)

app.include_router(produtos.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
