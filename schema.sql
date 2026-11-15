-- Cesta Solidaria — esquema do banco de dados (PostgreSQL)
-- O Flask-SQLAlchemy cria estas tabelas automaticamente no primeiro run
-- (db.create_all em app/__init__.py). Este script documenta o esquema
-- e pode ser usado para provisionar o banco manualmente.

CREATE TABLE IF NOT EXISTS doadores (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(120) NOT NULL,
    tipo        VARCHAR(2)   NOT NULL DEFAULT 'PF',
    email       VARCHAR(120),
    telefone    VARCHAR(20),
    criado_em   TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS doacoes (
    id                     SERIAL PRIMARY KEY,
    doador_id              INTEGER       NOT NULL REFERENCES doadores (id) ON DELETE CASCADE,
    descricao              VARCHAR(200)  NOT NULL,
    categoria              VARCHAR(20)   NOT NULL DEFAULT 'Alimento',
    quantidade             NUMERIC(10,2) NOT NULL CHECK (quantidade > 0),
    quantidade_disponivel  NUMERIC(10,2) NOT NULL CHECK (quantidade_disponivel >= 0),
    unidade                VARCHAR(5)    NOT NULL DEFAULT 'kg',
    data_validade          DATE,
    data_recebimento       DATE          NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS familias (
    id           SERIAL PRIMARY KEY,
    responsavel  VARCHAR(120) NOT NULL,
    telefone     VARCHAR(20),
    bairro       VARCHAR(120),
    qtd_membros  INTEGER      NOT NULL DEFAULT 1 CHECK (qtd_membros >= 1),
    cadastrado_em TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS distribuicoes (
    id                SERIAL PRIMARY KEY,
    familia_id        INTEGER       NOT NULL REFERENCES familias (id) ON DELETE CASCADE,
    doacao_id         INTEGER       NOT NULL REFERENCES doacoes (id) ON DELETE CASCADE,
    quantidade        NUMERIC(10,2) NOT NULL CHECK (quantidade > 0),
    data_distribuicao DATE          NOT NULL DEFAULT CURRENT_DATE,
    observacao        VARCHAR(200)
);

CREATE INDEX IF NOT EXISTS ix_doacoes_validade   ON doacoes (data_validade);
CREATE INDEX IF NOT EXISTS ix_distribuicoes_data ON distribuicoes (data_distribuicao);
