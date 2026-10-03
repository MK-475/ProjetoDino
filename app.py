import os
import uuid

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

import banco


app = Flask(__name__)

# Em desenvolvimento, os dados ficam dentro do projeto.
# Em hospedagem (ex.: Render), defina DATA_DIR=/var/data para usar
# um disco persistente para o SQLite e as imagens enviadas.
PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.environ.get("DATA_DIR", PASTA_PROJETO)
PASTA_UPLOADS = os.path.join(PASTA_DADOS, "uploads")

app.config["UPLOAD_FOLDER"] = PASTA_UPLOADS
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB por imagem


def preparar_dados():
    os.makedirs( PASTA_DADOS, exist_ok=True)
    os.makedirs( PASTA_UPLOADS, exist_ok=True)

    # Na primeira inicialização do servidor, copia o banco inicial
    # para o diretório persistente se ele ainda não existir.
    banco_inicial = os.path.join(PASTA_PROJETO, "dinossauros.db")
    banco_destino = os.path.join(PASTA_DADOS, "dinossauros.db")

    if PASTA_DADOS != PASTA_PROJETO and not os.path.exists(banco_destino):
        import shutil
        shutil.copy2(banco_inicial, banco_destino)


def caminho_imagem(nome_arquivo):
    if not nome_arquivo:
        return None

    return os.path.join(app.config["UPLOAD_FOLDER"], nome_arquivo)

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "gif", "webp"}


preparar_dados()
banco.criar_tabela()


def extensao_permitida(nome):
    return (
        "." in nome
        and nome.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS
    )


def salvar_imagem(arquivo):
    """
    Recebe a imagem enviada pelo formulário, salva em static/uploads
    e devolve somente o nome do arquivo para ser guardado no banco.
    """
    if not arquivo or arquivo.filename == "":
        return None

    if not extensao_permitida(arquivo.filename):
        return None

    nome_original = secure_filename(arquivo.filename)
    extensao = nome_original.rsplit(".", 1)[1].lower()

    # Nome único para evitar que uma foto substitua outra.
    nome_arquivo = f"{uuid.uuid4().hex}.{extensao}"

    arquivo.save(
        os.path.join(app.config["UPLOAD_FOLDER"], nome_arquivo)
    )

    return nome_arquivo


def apagar_imagem(nome_arquivo):
    if not nome_arquivo:
        return

    caminho = os.path.join(
        app.config["UPLOAD_FOLDER"],
        nome_arquivo
    )

    if os.path.isfile(caminho):
        os.remove(caminho)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/")
def inicio():
    dinossauros = banco.listar_dinossauros()
    total = banco.contar_dinossauros()

    return render_template(
        "index.html",
        dinossauros=dinossauros,
        total=total
    )


@app.route("/dinossauros")
def listar():
    dinossauros = banco.listar_dinossauros()

    return render_template(
        "listar.html",
        dinossauros=dinossauros
    )


@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    mensagem = None

    if request.method == "POST":
        nome = request.form["nome"].strip()
        idade = request.form["idade"].strip()
        especie = request.form["especie"].strip()
        arquivo = request.files.get("imagem")

        if not nome or not idade or not especie:
            mensagem = "Preencha todos os campos."

        elif arquivo and arquivo.filename and not extensao_permitida(arquivo.filename):
            mensagem = "Formato de imagem não permitido. Use JPG, JPEG, PNG, GIF ou WEBP."

        else:
            try:
                idade = int(idade)

                if idade <= 0:
                    mensagem = "A idade deve ser maior que zero."
                else:
                    imagem = salvar_imagem(arquivo)

                    banco.cadastrar_dinossauro(
                        nome,
                        idade,
                        especie,
                        imagem
                    )

                    return redirect(url_for("listar"))

            except ValueError:
                mensagem = "Digite uma idade válida."

    return render_template(
        "cadastrar.html",
        mensagem=mensagem,
        modo_edicao=False
    )


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    dinossauro = banco.buscar_dinossauro_por_id(id)

    if dinossauro is None:
        return redirect(url_for("listar"))

    mensagem = None

    if request.method == "POST":
        nome = request.form["nome"].strip()
        idade = request.form["idade"].strip()
        especie = request.form["especie"].strip()
        arquivo = request.files.get("imagem")

        if not nome or not idade or not especie:
            mensagem = "Preencha todos os campos."

        elif arquivo and arquivo.filename and not extensao_permitida(arquivo.filename):
            mensagem = "Formato de imagem não permitido. Use JPG, JPEG, PNG, GIF ou WEBP."

        else:
            try:
                idade = int(idade)

                if idade <= 0:
                    mensagem = "A idade deve ser maior que zero."

                else:
                    imagem = None

                    # Só troca a imagem se o usuário escolher uma nova.
                    if arquivo and arquivo.filename:
                        imagem = salvar_imagem(arquivo)

                        if imagem is not None:
                            apagar_imagem(dinossauro["imagem"])

                    banco.atualizar_dinossauro(
                        id,
                        nome,
                        idade,
                        especie,
                        imagem
                    )

                    return redirect(url_for("listar"))

            except ValueError:
                mensagem = "Digite uma idade válida."

    return render_template(
        "cadastrar.html",
        dinossauro=dinossauro,
        mensagem=mensagem,
        modo_edicao=True
    )


@app.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    dinossauro = banco.buscar_dinossauro_por_id(id)

    if dinossauro is not None:
        apagar_imagem(dinossauro["imagem"])
        banco.excluir_dinossauro(id)

    return redirect(url_for("listar"))


@app.errorhandler(413)
def arquivo_muito_grande(error):
    return render_template(
        "cadastrar.html",
        mensagem="A imagem é muito grande. O limite é de 5 MB.",
        modo_edicao=False
    ), 413


if __name__ == "__main__":
    preparar_dados()
    banco.criar_tabela()

    # Local: http://127.0.0.1:5000
    # Em produção, o Render usa Gunicorn (gunicorn app:app).
    app.run(debug=True)
