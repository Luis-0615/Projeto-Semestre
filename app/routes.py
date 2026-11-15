from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from . import db
from .models import Distribuicao, Doacao, Doador, Familia

bp = Blueprint("main", __name__)

LIMITE_VALIDADE_DIAS = 7


def _parse_decimal(valor: str) -> Decimal | None:
    try:
        numero = Decimal((valor or "").replace(",", "."))
    except InvalidOperation:
        return None
    return numero if numero > 0 else None


def _parse_date(valor: str) -> date | None:
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        return None


# ---------------------------------------------------------------- dashboard


@bp.get("/")
def index():
    totais = {
        "doadores": Doador.query.count(),
        "doacoes": Doacao.query.count(),
        "familias": Familia.query.count(),
        "distribuicoes": Distribuicao.query.count(),
    }
    limite = date.today() + timedelta(days=LIMITE_VALIDADE_DIAS)
    vencendo = (
        Doacao.query.filter(
            Doacao.data_validade.isnot(None),
            Doacao.data_validade <= limite,
            Doacao.quantidade_disponivel > 0,
        )
        .order_by(Doacao.data_validade)
        .all()
    )
    ultimas = Doacao.query.order_by(Doacao.id.desc()).limit(5).all()
    return render_template(
        "index.html", totais=totais, vencendo=vencendo, ultimas=ultimas
    )


# ----------------------------------------------------------------- doadores


@bp.get("/doadores")
def doadores():
    lista = Doador.query.order_by(Doador.nome).all()
    return render_template("doadores.html", doadores=lista)


@bp.route("/doadores/novo", methods=["GET", "POST"])
def doador_novo():
    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        tipo = request.form.get("tipo", "PF")
        if not nome or tipo not in ("PF", "PJ"):
            flash("Informe o nome e um tipo valido (PF ou PJ).", "erro")
            return redirect(url_for("main.doador_novo"))
        doador = Doador(
            nome=nome,
            tipo=tipo,
            email=(request.form.get("email") or "").strip() or None,
            telefone=(request.form.get("telefone") or "").strip() or None,
        )
        db.session.add(doador)
        db.session.commit()
        flash("Doador cadastrado com sucesso.", "ok")
        return redirect(url_for("main.doadores"))
    return render_template("doador_form.html")


@bp.post("/doadores/<int:doador_id>/excluir")
def doador_excluir(doador_id: int):
    doador = Doador.query.get_or_404(doador_id)
    db.session.delete(doador)
    db.session.commit()
    flash("Doador removido.", "ok")
    return redirect(url_for("main.doadores"))


# ------------------------------------------------------------------ doacoes


@bp.get("/doacoes")
def doacoes():
    lista = Doacao.query.order_by(Doacao.data_recebimento.desc()).all()
    return render_template("doacoes.html", doacoes=lista)


@bp.route("/doacoes/novo", methods=["GET", "POST"])
def doacao_nova():
    if request.method == "POST":
        descricao = (request.form.get("descricao") or "").strip()
        quantidade = _parse_decimal(request.form.get("quantidade", ""))
        doador = db.session.get(Doador, request.form.get("doador_id", type=int))
        categoria = request.form.get("categoria", "Alimento")
        unidade = request.form.get("unidade", "kg")
        validade = _parse_date(request.form.get("data_validade", ""))

        if not descricao or quantidade is None or doador is None:
            flash("Preencha descricao, doador e uma quantidade maior que zero.", "erro")
            return redirect(url_for("main.doacao_nova"))
        if categoria not in Doacao.CATEGORIAS or unidade not in Doacao.UNIDADES:
            flash("Categoria ou unidade invalida.", "erro")
            return redirect(url_for("main.doacao_nova"))

        doacao = Doacao(
            doador=doador,
            descricao=descricao,
            categoria=categoria,
            quantidade=quantidade,
            quantidade_disponivel=quantidade,
            unidade=unidade,
            data_validade=validade,
        )
        db.session.add(doacao)
        db.session.commit()
        flash("Doacao registrada com sucesso.", "ok")
        return redirect(url_for("main.doacoes"))

    return render_template(
        "doacao_form.html",
        doadores=Doador.query.order_by(Doador.nome).all(),
        categorias=Doacao.CATEGORIAS,
        unidades=Doacao.UNIDADES,
    )


@bp.post("/doacoes/<int:doacao_id>/excluir")
def doacao_excluir(doacao_id: int):
    doacao = Doacao.query.get_or_404(doacao_id)
    db.session.delete(doacao)
    db.session.commit()
    flash("Doacao removida.", "ok")
    return redirect(url_for("main.doacoes"))


# ----------------------------------------------------------------- familias


@bp.get("/familias")
def familias():
    lista = Familia.query.order_by(Familia.responsavel).all()
    return render_template("familias.html", familias=lista)


@bp.route("/familias/novo", methods=["GET", "POST"])
def familia_nova():
    if request.method == "POST":
        responsavel = (request.form.get("responsavel") or "").strip()
        qtd_membros = request.form.get("qtd_membros", type=int) or 0
        if not responsavel or qtd_membros < 1:
            flash("Informe o responsavel e o numero de membros (minimo 1).", "erro")
            return redirect(url_for("main.familia_nova"))
        familia = Familia(
            responsavel=responsavel,
            telefone=(request.form.get("telefone") or "").strip() or None,
            bairro=(request.form.get("bairro") or "").strip() or None,
            qtd_membros=qtd_membros,
        )
        db.session.add(familia)
        db.session.commit()
        flash("Familia cadastrada com sucesso.", "ok")
        return redirect(url_for("main.familias"))
    return render_template("familia_form.html")


@bp.post("/familias/<int:familia_id>/excluir")
def familia_excluir(familia_id: int):
    familia = Familia.query.get_or_404(familia_id)
    db.session.delete(familia)
    db.session.commit()
    flash("Familia removida.", "ok")
    return redirect(url_for("main.familias"))


# ------------------------------------------------------------ distribuicoes


@bp.get("/distribuicoes")
def distribuicoes():
    lista = Distribuicao.query.order_by(
        Distribuicao.data_distribuicao.desc(), Distribuicao.id.desc()
    ).all()
    return render_template("distribuicoes.html", distribuicoes=lista)


@bp.route("/distribuicoes/novo", methods=["GET", "POST"])
def distribuicao_nova():
    if request.method == "POST":
        familia = db.session.get(Familia, request.form.get("familia_id", type=int))
        doacao = db.session.get(Doacao, request.form.get("doacao_id", type=int))
        quantidade = _parse_decimal(request.form.get("quantidade", ""))

        if familia is None or doacao is None or quantidade is None:
            flash("Selecione a familia, a doacao e uma quantidade maior que zero.", "erro")
            return redirect(url_for("main.distribuicao_nova"))
        if quantidade > doacao.quantidade_disponivel:
            flash(
                f"Quantidade indisponivel: restam "
                f"{doacao.quantidade_disponivel} {doacao.unidade} de "
                f"'{doacao.descricao}'.",
                "erro",
            )
            return redirect(url_for("main.distribuicao_nova"))

        doacao.quantidade_disponivel = doacao.quantidade_disponivel - quantidade
        distribuicao = Distribuicao(
            familia=familia,
            doacao=doacao,
            quantidade=quantidade,
            observacao=(request.form.get("observacao") or "").strip() or None,
        )
        db.session.add(distribuicao)
        db.session.commit()
        flash("Distribuicao registrada com sucesso.", "ok")
        return redirect(url_for("main.distribuicoes"))

    return render_template(
        "distribuicao_form.html",
        familias=Familia.query.order_by(Familia.responsavel).all(),
        doacoes=Doacao.query.filter(Doacao.quantidade_disponivel > 0)
        .order_by(Doacao.descricao)
        .all(),
    )


# ---------------------------------------------------------------------- API


@bp.get("/api/resumo")
def api_resumo():
    return jsonify(
        {
            "doadores": Doador.query.count(),
            "doacoes": Doacao.query.count(),
            "familias": Familia.query.count(),
            "distribuicoes": Distribuicao.query.count(),
        }
    )


@bp.get("/api/doacoes")
def api_doacoes():
    doacoes = Doacao.query.order_by(Doacao.id).all()
    return jsonify(
        [
            {
                "id": d.id,
                "descricao": d.descricao,
                "categoria": d.categoria,
                "quantidade": float(d.quantidade),
                "quantidade_disponivel": float(d.quantidade_disponivel),
                "unidade": d.unidade,
                "doador": d.doador.nome,
                "data_validade": d.data_validade.isoformat()
                if d.data_validade
                else None,
            }
            for d in doacoes
        ]
  )
