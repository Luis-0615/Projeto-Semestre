"""Testes de integracao do Cesta Solidaria.

Usam um banco PostgreSQL de teste real (cestasolidaria_test). Aponte
TEST_DATABASE_URL para outro banco se necessario.
"""

import os
from decimal import Decimal

import pytest

from app import create_app, db
from app.models import Distribuicao, Doacao, Doador, Familia

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/cestasolidaria_test",
)


@pytest.fixture()
def app():
    app = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URL}
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def _criar_doador(client, nome="Mercado Bom Vizinho"):
    resp = client.post(
        "/doadores/novo",
        data={"nome": nome, "tipo": "PJ", "email": "contato@bomvizinho.com"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    return Doador.query.filter_by(nome=nome).one()


def _criar_doacao(client, doador, quantidade="10", descricao="Arroz tipo 1"):
    resp = client.post(
        "/doacoes/novo",
        data={
            "descricao": descricao,
            "doador_id": doador.id,
            "quantidade": quantidade,
            "unidade": "kg",
            "categoria": "Alimento",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    return Doacao.query.filter_by(descricao=descricao).one()


def _criar_familia(client, responsavel="Maria Silva"):
    resp = client.post(
        "/familias/novo",
        data={"responsavel": responsavel, "qtd_membros": 4, "bairro": "Jardim das Flores"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    return Familia.query.filter_by(responsavel=responsavel).one()


def test_dashboard_responde(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Painel da ONG" in resp.get_data(as_text=True)


def test_cadastro_doador(client):
    doador = _criar_doador(client)
    assert doador.tipo == "PJ"
    resp = client.get("/doadores")
    assert "Mercado Bom Vizinho" in resp.get_data(as_text=True)


def test_cadastro_doador_sem_nome_falha(client):
    resp = client.post(
        "/doadores/novo", data={"nome": "", "tipo": "PF"}, follow_redirects=True
    )
    assert resp.status_code == 200
    assert Doador.query.count() == 0


def test_cadastro_doacao_vinculada_a_doador(client):
    doador = _criar_doador(client)
    doacao = _criar_doacao(client, doador)
    assert doacao.quantidade == Decimal("10")
    assert doacao.quantidade_disponivel == Decimal("10")
    assert doacao.doador == doador


def test_doacao_quantidade_invalida_falha(client):
    doador = _criar_doador(client)
    client.post(
        "/doacoes/novo",
        data={"descricao": "Feijao", "doador_id": doador.id, "quantidade": "abc"},
        follow_redirects=True,
    )
    assert Doacao.query.count() == 0


def test_cadastro_familia(client):
    familia = _criar_familia(client)
    assert familia.qtd_membros == 4


def test_distribuicao_decrementa_estoque(client):
    doador = _criar_doador(client)
    doacao = _criar_doacao(client, doador)
    familia = _criar_familia(client)

    resp = client.post(
        "/distribuicoes/novo",
        data={"familia_id": familia.id, "doacao_id": doacao.id, "quantidade": "3"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    db.session.refresh(doacao)
    assert doacao.quantidade_disponivel == Decimal("7")
    assert Distribuicao.query.count() == 1


def test_distribuicao_acima_do_estoque_falha(client):
    doador = _criar_doador(client)
    doacao = _criar_doacao(client, doador)
    familia = _criar_familia(client)

    resp = client.post(
        "/distribuicoes/novo",
        data={"familia_id": familia.id, "doacao_id": doacao.id, "quantidade": "99"},
        follow_redirects=True,
    )
    assert "indisponivel" in resp.get_data(as_text=True)
    db.session.refresh(doacao)
    assert doacao.quantidade_disponivel == Decimal("10")
    assert Distribuicao.query.count() == 0


def test_api_resumo(client):
    _criar_doador(client)
    _criar_familia(client)
    dados = client.get("/api/resumo").get_json()
    assert dados == {"doadores": 1, "doacoes": 0, "familias": 1, "distribuicoes": 0}


def test_api_doacoes(client):
    doador = _criar_doador(client)
    _criar_doacao(client, doador)
    dados = client.get("/api/doacoes").get_json()
    assert len(dados) == 1
    assert dados[0]["descricao"] == "Arroz tipo 1"
    assert dados[0]["doador"] == "Mercado Bom Vizinho"
