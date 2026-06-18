# API de Produtos — Estrutura Modular

Mesma API de gerenciamento de produtos, agora organizada em módulos separados por responsabilidade. Cada camada tem um único propósito e pode ser alterada sem impactar as demais.

---

## Diferença arquitetural em relação à versão monolítica

| Aspecto | Versão anterior (main.py único) | Esta versão (modular) |
|---|---|---|
| Organização | Tudo em `main.py` | Camadas separadas em `app/` |
| ORM | Definido junto com as rotas | `app/models.py` isolado |
| Schemas | Definido junto com as rotas | `app/schemas.py` isolado |
| Banco | Configurado em `main.py` | `app/database.py` isolado |
| Rotas | Funções soltas em `main.py` | `APIRouter` em `app/routers/produtos.py` |
| `main.py` | ~100 linhas | ~12 linhas (só monta a app) |

Essa separação segue o princípio da responsabilidade única: se a regra de negócio mudar, edita-se `models.py`; se o schema de resposta mudar, edita-se `schemas.py` — sem riscos de quebrar outra camada.

---

## Estrutura do repositório

```
ecommerce_v2/
├── main.py                    # Ponto de entrada — monta a app e inclui routers
├── conftest.py                # Fixtures pytest
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── README.md
├── app/
│   ├── __init__.py
│   ├── database.py            # engine, SessionLocal, Base, get_db
│   ├── models.py              # Modelo ORM Produto
│   ├── schemas.py             # ProdutoCreate, ProdutoResponse (Pydantic)
│   └── routers/
│       ├── __init__.py
│       └── produtos.py        # APIRouter com os 4 endpoints
└── tests/
    ├── __init__.py
    └── test_produtos.py       # 18 funções de teste
```

---

## Subindo o banco de dados

```bash
# Apenas o banco de testes (necessário para rodar pytest)
docker-compose up -d db_test

# Ambos os bancos (dev + test)
docker-compose up -d
```

Aguarde o status `healthy` antes de rodar os testes:

```bash
docker-compose ps
```

---

## Instalando dependências

```bash
pip install -r requirements.txt
```

---

## Executando os testes

```bash
# Comando completo recomendado
docker-compose up -d db_test && pytest

# Parar no primeiro erro
pytest -v -x

# Com cobertura detalhada
pytest --cov=app --cov=main --cov-report=term-missing

# Verificação final antes da entrega
docker-compose up -d db_test && pytest --cov=app --cov=main -v
```

---

## Saída esperada do pytest

```
============================================================= test session starts ==============================================================
platform linux -- Python 3.12.x, pytest-8.3.4
configfile: pytest.ini
collected 18 items

tests/test_produtos.py::test_listar_produtos_banco_vazio PASSED                         [  5%]
tests/test_produtos.py::test_listar_retorna_todos_os_criados PASSED                     [ 11%]
tests/test_produtos.py::test_criar_produto_retorna_201_e_id PASSED                      [ 16%]
tests/test_produtos.py::test_criar_produto_persiste_e_aparece_na_listagem PASSED        [ 22%]
tests/test_produtos.py::test_criar_produto_valores_padrao PASSED                        [ 27%]
tests/test_produtos.py::test_buscar_produto_existente PASSED                            [ 33%]
tests/test_produtos.py::test_buscar_produto_inexistente_retorna_404 PASSED              [ 38%]
tests/test_produtos.py::test_deletar_produto_retorna_204_sem_body PASSED                [ 44%]
tests/test_produtos.py::test_deletar_produto_e_confirmar_via_get PASSED                 [ 50%]
tests/test_produtos.py::test_deletar_produto_inexistente_retorna_404 PASSED             [ 55%]
tests/test_produtos.py::test_payload_invalido_retorna_422[nome_vazio] PASSED            [ 61%]
tests/test_produtos.py::test_payload_invalido_retorna_422[nome_so_espacos] PASSED       [ 66%]
tests/test_produtos.py::test_payload_invalido_retorna_422[preco_zero] PASSED            [ 72%]
tests/test_produtos.py::test_payload_invalido_retorna_422[preco_negativo] PASSED        [ 77%]
tests/test_produtos.py::test_payload_invalido_retorna_422[sem_nome] PASSED              [ 83%]
tests/test_produtos.py::test_payload_invalido_retorna_422[sem_preco] PASSED             [ 88%]
tests/test_produtos.py::test_payload_invalido_retorna_422[estoque_negativo] PASSED      [ 94%]
tests/test_produtos.py::test_banco_isolado_comeca_vazio PASSED                         [100%]

---------- coverage: platform linux, python 3.12 ----------
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
app/database.py                12      1    92%
app/models.py                   8      0   100%
app/routers/produtos.py        24      0   100%
app/schemas.py                 14      0   100%
main.py                         7      0   100%
---------------------------------------------------------
TOTAL                          65      1    98%

============================================================= 18 passed in 3.87s ===============================================================
```

---

## Como o isolamento entre testes funciona

A fixture `client` em `conftest.py` segue o ciclo:

```
ANTES  →  Base.metadata.create_all(test_engine)     # tabelas do zero
DURANTE →  dependency_overrides[get_db] = _override  # banco de teste injetado
           yield TestClient(app)                      # teste executa aqui
DEPOIS  →  dependency_overrides.clear()              # remove override
           Base.metadata.drop_all(test_engine)        # destrói tudo
```

Como `get_db` está em `app/database.py` (separado do router), o override é aplicado de forma limpa sem monkeypatching — qualquer endpoint que use `Depends(get_db)` automaticamente recebe a sessão de teste.

---

## Rodando a API localmente

```bash
docker-compose up -d db
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ecommerce uvicorn main:app --reload
```

Acesse `http://localhost:8000/docs` para a interface Swagger UI.

## Endpoints

| Método | Rota | Status | Descrição |
|--------|------|--------|-----------|
| `GET` | `/produtos/` | 200 | Lista todos os produtos |
| `POST` | `/produtos/` | 201 | Cria novo produto |
| `GET` | `/produtos/{id}` | 200 / 404 | Busca por id |
| `DELETE` | `/produtos/{id}` | 204 / 404 | Remove por id |
