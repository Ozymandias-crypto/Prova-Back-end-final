from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    preco: float = Field(..., gt=0)
    estoque: int = Field(default=0, ge=0)
    ativo: bool = Field(default=True)

    @field_validator("nome")
    @classmethod
    def nome_nao_pode_ser_branco(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Nome não pode conter apenas espaços em branco")
        return v.strip()


class ProdutoResponse(ProdutoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
