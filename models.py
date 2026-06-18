from sqlalchemy import Boolean, Column, Float, Integer, String

from app.database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
