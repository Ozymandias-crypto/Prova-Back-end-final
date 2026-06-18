"""
conftest.py — Fixtures de teste para a estrutura modular.

Isolamento: create_all antes / drop_all depois de cada teste.
A sessão de produção é substituída via dependency_overrides,
sem tocar em nenhum arquivo do módulo app/.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/ecommerce_test",
)

test_engine = create_engine(TEST_DATABASE_URL)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)

    def _override():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def produto_existente(client: TestClient) -> dict:
    resp = client.post(
        "/produtos/",
        json={"nome": "Teclado Mecânico", "preco": 349.90, "estoque": 10},
    )
    assert resp.status_code == 201
    return resp.json()
