from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Produto
from app.schemas import ProdutoCreate, ProdutoResponse

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("/", response_model=list[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).all()


@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(payload: ProdutoCreate, db: Session = Depends(get_db)):
    produto = Produto(**payload.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


@router.get("/{produto_id}", response_model=ProdutoResponse)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto {produto_id} não encontrado.",
        )
    return produto


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto {produto_id} não encontrado.",
        )
    db.delete(produto)
    db.commit()
