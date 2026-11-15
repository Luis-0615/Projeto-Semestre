# Cesta Solidária

Plataforma web para gestão de doações de alimentos e itens essenciais de uma
ONG comunitária. Permite cadastrar **doadores**, registrar **doações** com
controle de estoque e validade, cadastrar **famílias beneficiadas** e
registrar **distribuições**, com baixa automática no estoque.

Projeto desenvolvido como Projeto de Extensão em Desenvolvimento de Software
(UNINOVE), em parceria com a ONG comunitária **Mãos que Alimentam**.

## Stack

- **Linguagem:** Python 3.10+
- **Framework:** Flask 3 (rotas web + API JSON)
- **ORM:** Flask-SQLAlchemy
- **Banco de dados:** PostgreSQL
- **Testes:** pytest (testes de integração sobre banco real)
- **Frontend:** Jinja2 + CSS próprio (responsivo, sem dependências externas)

## Funcionalidades

- Painel com totais de doadores, doações, famílias e distribuições
- Alerta de itens próximos do vencimento (7 dias)
- CRUD de doadores (pessoa física ou jurídica)
- Registro de doações com categoria, unidade, quantidade e data de validade
- Cadastro de famílias beneficiadas (responsável, bairro, nº de membros)
- Registro de distribuições com validação de estoque disponível
- API JSON: `GET /api/resumo` e `GET /api/doacoes`

## Como executar

### 1. Suba o PostgreSQL

Com Docker (recomendado):

```bash
docker compose up -d
```

Ou use um PostgreSQL local já instalado e crie o banco:

```bash
createdb cestasolidaria
psql cestasolidaria < schema.sql   # opcional: o app cria as tabelas sozinho
```

### 2. Instale as dependências e rode a aplicação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Acesse <http://localhost:5000>.

### Configuração

| Variável        | Padrão                                                              | Descrição            |
| --------------- | ------------------------------------------------------------------- | -------------------- |
| `DATABASE_URL`  | `postgresql+psycopg2://postgres:postgres@localhost:5432/cestasolidaria` | Conexão com o banco  |
| `SECRET_KEY`    | `dev-secret-key`                                                    | Chave de sessão Flask |

## Testes

```bash
createdb cestasolidaria_test   # uma vez
pip install -r requirements-dev.txt
TEST_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/cestasolidaria_test" pytest -v
```

Os testes criam e destroem as tabelas no banco de teste a cada cenário.

## Estrutura

```
cesta-solidaria/
├── app/
│   ├── __init__.py        # application factory + configuração do banco
│   ├── models.py          # Doador, Doacao, Familia, Distribuicao
│   ├── routes.py          # rotas web (HTML) e API JSON
│   ├── static/style.css
│   └── templates/         # páginas Jinja2
├── tests/test_app.py      # testes de integração (pytest)
├── schema.sql             # esquema documentado do banco
├── docker-compose.yml     # PostgreSQL pronto para uso
├── requirements.txt
├── requirements-dev.txt
└── run.py                 # ponto de entrada
```

## Licença

MIT — veja [LICENSE](LICENSE).
