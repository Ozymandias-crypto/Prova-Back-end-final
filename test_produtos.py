"""
tests/test_produtos.py — Suíte de testes para a estrutura modular.

Rotas com prefixo /produtos/ (barra final incluída pelo APIRouter).
"""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Listagem
# ---------------------------------------------------------------------------


def test_listar_produtos_banco_vazio(client: TestClient):
    resp = client.get("/produtos/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_listar_retorna_todos_os_criados(client: TestClient):
    client.post("/produtos/", json={"nome": "Produto A", "preco": 10.0})
    client.post("/produtos/", json={"nome": "Produto B", "preco": 20.0})

    resp = client.get("/produtos/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# ---------------------------------------------------------------------------
# Criação
# ---------------------------------------------------------------------------


def test_criar_produto_retorna_201_e_id(client: TestClient):
    payload = {"nome": "Monitor 4K", "preco": 2499.00, "estoque": 3}
    resp = client.post("/produtos/", json=payload)

    assert resp.status_code == 201
    data = resp.json()
    assert isinstance(data["id"], int)
    assert data["nome"] == "Monitor 4K"
    assert data["preco"] == 2499.00


def test_criar_produto_persiste_e_aparece_na_listagem(client: TestClient):
    post = client.post("/produtos/", json={"nome": "Webcam HD", "preco": 180.0})
    produto_id = post.json()["id"]

    lista = client.get("/produtos/").json()
    assert any(p["id"] == produto_id for p in lista)


def test_criar_produto_valores_padrao(client: TestClient):
    resp = client.post("/produtos/", json={"nome": "Cabo HDMI", "preco": 39.90})
    data = resp.json()

    assert data["estoque"] == 0
    assert data["ativo"] is True


# ---------------------------------------------------------------------------
# Busca por id
# ---------------------------------------------------------------------------


def test_buscar_produto_existente(client: TestClient, produto_existente: dict):
    pid = produto_existente["id"]
    resp = client.get(f"/produtos/{pid}")

    assert resp.status_code == 200
    assert resp.json()["id"] == pid
    assert resp.json()["nome"] == produto_existente["nome"]


def test_buscar_produto_inexistente_retorna_404(client: TestClient):
    resp = client.get("/produtos/99999")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Deleção
# ---------------------------------------------------------------------------


def test_deletar_produto_retorna_204_sem_body(client: TestClient, produto_existente: dict):
    pid = produto_existente["id"]
    resp = client.delete(f"/produtos/{pid}")

    assert resp.status_code == 204
    assert resp.content == b""


def test_deletar_produto_e_confirmar_via_get(client: TestClient, produto_existente: dict):
    pid = produto_existente["id"]
    client.delete(f"/produtos/{pid}")

    resp = client.get(f"/produtos/{pid}")
    assert resp.status_code == 404


def test_deletar_produto_inexistente_retorna_404(client: TestClient):
    resp = client.delete("/produtos/99999")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Validação de payload — parametrizado (422)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"nome": "", "preco": 50.0}, id="nome_vazio"),
        pytest.param({"nome": "   ", "preco": 50.0}, id="nome_so_espacos"),
        pytest.param({"nome": "Produto", "preco": 0}, id="preco_zero"),
        pytest.param({"nome": "Produto", "preco": -1}, id="preco_negativo"),
        pytest.param({"preco": 50.0}, id="sem_nome"),
        pytest.param({"nome": "Produto"}, id="sem_preco"),
        pytest.param({"nome": "Produto", "preco": 10.0, "estoque": -1}, id="estoque_negativo"),
    ],
)
def test_payload_invalido_retorna_422(client: TestClient, payload: dict):
    resp = client.post("/produtos/", json=payload)
    assert resp.status_code == 422, f"Esperado 422, recebido {resp.status_code}. Payload: {payload}"


# ---------------------------------------------------------------------------
# Isolamento de banco
# ---------------------------------------------------------------------------


def test_banco_isolado_comeca_vazio(client: TestClient):
    """Garante que nenhum dado de outro teste vazou para esta execução."""
    resp = client.get("/produtos/")
    assert resp.json() == [], "Banco não estava isolado — dados de outro teste vazaram."
