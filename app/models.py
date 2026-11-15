from datetime import date, datetime

from . import db


class Doador(db.Model):
    """Pessoa fisica ou juridica que doa itens para a ONG."""

    __tablename__ = "doadores"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(2), nullable=False, default="PF")  # PF ou PJ
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    doacoes = db.relationship(
        "Doacao", back_populates="doador", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Doador {self.nome}>"


class Doacao(db.Model):
    """Item doado (alimento, higiene, roupa etc.) com controle de estoque."""

    __tablename__ = "doacoes"

    CATEGORIAS = ("Alimento", "Higiene", "Limpeza", "Roupa", "Outros")
    UNIDADES = ("kg", "un", "cx", "lt")

    id = db.Column(db.Integer, primary_key=True)
    doador_id = db.Column(
        db.Integer, db.ForeignKey("doadores.id"), nullable=False
    )
    descricao = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(20), nullable=False, default="Alimento")
    quantidade = db.Column(db.Numeric(10, 2), nullable=False)
    quantidade_disponivel = db.Column(db.Numeric(10, 2), nullable=False)
    unidade = db.Column(db.String(5), nullable=False, default="kg")
    data_validade = db.Column(db.Date)
    data_recebimento = db.Column(db.Date, nullable=False, default=date.today)

    doador = db.relationship("Doador", back_populates="doacoes")
    distribuicoes = db.relationship(
        "Distribuicao", back_populates="doacao", cascade="all, delete-orphan"
    )

    def dias_para_vencer(self) -> int | None:
        if self.data_validade is None:
            return None
        return (self.data_validade - date.today()).days

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Doacao {self.descricao}>"


class Familia(db.Model):
    """Familia beneficiada cadastrada pela ONG."""

    __tablename__ = "familias"

    id = db.Column(db.Integer, primary_key=True)
    responsavel = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20))
    bairro = db.Column(db.String(120))
    qtd_membros = db.Column(db.Integer, nullable=False, default=1)
    cadastrado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    distribuicoes = db.relationship(
        "Distribuicao", back_populates="familia", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Familia {self.responsavel}>"


class Distribuicao(db.Model):
    """Saida de itens do estoque para uma familia beneficiada."""

    __tablename__ = "distribuicoes"

    id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(
        db.Integer, db.ForeignKey("familias.id"), nullable=False
    )
    doacao_id = db.Column(
        db.Integer, db.ForeignKey("doacoes.id"), nullable=False
    )
    quantidade = db.Column(db.Numeric(10, 2), nullable=False)
    data_distribuicao = db.Column(db.Date, nullable=False, default=date.today)
    observacao = db.Column(db.String(200))

    familia = db.relationship("Familia", back_populates="distribuicoes")
    doacao = db.relationship("Doacao", back_populates="distribuicoes")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Distribuicao {self.id}>"
