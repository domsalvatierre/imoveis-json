from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
import os
import bcrypt
from datetime import datetime, timedelta

app = Flask(__name__)

# 🔑 SECRET KEY
app.secret_key = os.environ.get("SECRET_KEY", "chave_padrao_insegura")

# 🔐 CONFIGURAÇÕES DE SESSÃO
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False  # True em produção (HTTPS)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)

# 📁 Pasta de arquivos
PASTA_ARQUIVOS = "arquivos"

# 🔐 SENHAS
USUARIOS = {
    "CM": bcrypt.hashpw("Cm@8392!".encode(), bcrypt.gensalt()),
    "FDT": bcrypt.hashpw("Fd@1234!".encode(), bcrypt.gensalt()),
    "MANAUSCULT": bcrypt.hashpw("Mc#4721!".encode(), bcrypt.gensalt()),
    "SEMACC": bcrypt.hashpw("Sa$9182!".encode(), bcrypt.gensalt()),
    "SEMED": bcrypt.hashpw("Sd%2746!".encode(), bcrypt.gensalt()),
    "SEMINF": bcrypt.hashpw("Si&5931!".encode(), bcrypt.gensalt()),
    "SEMSA": bcrypt.hashpw("Ss*8472!".encode(), bcrypt.gensalt()),
    "SEMULSP": bcrypt.hashpw("Su@6291!".encode(), bcrypt.gensalt()),
    "IMMU": bcrypt.hashpw("Im#3758!".encode(), bcrypt.gensalt()),
    "MANAUSPREV": bcrypt.hashpw("Mp$4829!".encode(), bcrypt.gensalt()),
    "SEMAD": bcrypt.hashpw("Sa&9517!".encode(), bcrypt.gensalt()),
    "SEMEF": bcrypt.hashpw("Sf*2638!".encode(), bcrypt.gensalt()),
    "SEMJEL": bcrypt.hashpw("Sj@7405!".encode(), bcrypt.gensalt()),
    "SEMSEG": bcrypt.hashpw("Sg#1864!".encode(), bcrypt.gensalt()),
    "IMPLURB": bcrypt.hashpw("Il$5297!".encode(), bcrypt.gensalt()),
    "PGM": bcrypt.hashpw("Pg%8142!".encode(), bcrypt.gensalt()),
    "SEMASC": bcrypt.hashpw("Sc&3975!".encode(), bcrypt.gensalt()),
    "SEMHAF": bcrypt.hashpw("Sh*6481!".encode(), bcrypt.gensalt()),
    "SEMMAS": bcrypt.hashpw("Sm@2759!".encode(), bcrypt.gensalt()),
    "SEMTEPI": bcrypt.hashpw("St#9306!".encode(), bcrypt.gensalt())
}

# 🛡️ Controle de tentativas
tentativas = {}
bloqueios = {}

TEMPO_BLOQUEIO = timedelta(minutes=5)

# 🧾 Log
def registrar_log(ug, acao):
    with open("logs.txt", "a") as f:
        f.write(f"{datetime.now()} - {ug} - {acao}\n")


# 🔐 LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ug = request.form["ug"].strip().upper()
        senha = request.form["senha"]

        # valida UG
        if ug not in USUARIOS:
            return render_template("erro.html", mensagem="UG inválida")

        # verifica bloqueio
        if ug in bloqueios:
            if datetime.now() < bloqueios[ug]:
                tempo_restante = (bloqueios[ug] - datetime.now()).seconds
                return render_template("bloqueado.html", tempo=tempo_restante)
            else:
                del bloqueios[ug]
                tentativas[ug] = 0

        # inicializa tentativas
        if ug not in tentativas:
            tentativas[ug] = 0

        # valida senha
        if bcrypt.checkpw(senha.encode(), USUARIOS[ug]):
            session["ug"] = ug
            tentativas[ug] = 0
            registrar_log(ug, "LOGIN OK")
            return redirect(url_for("painel"))
        else:
            tentativas[ug] += 1
            registrar_log(ug, "LOGIN FALHOU")

            if tentativas[ug] >= 3:
                bloqueios[ug] = datetime.now() + TEMPO_BLOQUEIO
                registrar_log(ug, "CONTA BLOQUEADA")
                return render_template("bloqueado.html", tempo=300)

            return render_template("erro.html", mensagem=f"Senha incorreta ({tentativas[ug]}/3)")

    return render_template("login.html")


# 📊 PAINEL
@app.route("/painel")
def painel():
    if "ug" not in session:
        return redirect(url_for("login"))

    return render_template("painel.html", ug=session["ug"])


# 📥 DOWNLOAD JSON
@app.route("/download/json")
def download_json():
    if "ug" not in session:
        return redirect(url_for("login"))

    ug = session["ug"]
    pasta = os.path.join(PASTA_ARQUIVOS, ug)

    if not os.path.exists(pasta):
        return render_template("erro.html", mensagem="Pasta da UG não encontrada")

    arquivos = os.listdir(pasta)
    json_file = [f for f in arquivos if f.endswith(".json")]

    if not json_file:
        return render_template("erro.html", mensagem="Arquivo JSON não encontrado")

    registrar_log(ug, "DOWNLOAD JSON")
    return send_from_directory(pasta, json_file[0], as_attachment=True)


# 📄 DOWNLOAD EXCEL
@app.route("/download/excel")
def download_excel():
    if "ug" not in session:
        return redirect(url_for("login"))

    ug = session["ug"]
    pasta = os.path.join(PASTA_ARQUIVOS, ug)

    if not os.path.exists(pasta):
        return render_template("erro.html", mensagem="Pasta da UG não encontrada")

    arquivos = os.listdir(pasta)
    excel_file = [f for f in arquivos if f.endswith(".xlsx")]

    if not excel_file:
        return render_template("erro.html", mensagem="Arquivo Excel não encontrado")

    registrar_log(ug, "DOWNLOAD EXCEL")
    return send_from_directory(pasta, excel_file[0], as_attachment=True)


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# 🛑 ERROS GLOBAIS

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template("erro.html", mensagem="Página não encontrada"), 404


@app.errorhandler(500)
def erro_interno(e):
    return render_template("erro.html", mensagem="Erro interno do servidor"), 500


if __name__ == "__main__":
    app.run()