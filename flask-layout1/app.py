import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-secreta-da-atividade")

DATABASE = "dados.db"


def conectar():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    return conexao


def iniciar_banco():
    conexao = conectar()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    """)

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            sobrenome TEXT NOT NULL,
            idade INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            disciplina TEXT NOT NULL,
            nota REAL NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    usuario = conexao.execute(
        "SELECT id FROM usuarios WHERE usuario = ?",
        ("felipe",)
    ).fetchone()

    if not usuario:
        senha_hash = generate_password_hash("1234")
        cursor = conexao.execute(
            "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
            ("felipe", senha_hash)
        )
        usuario_id = cursor.lastrowid

        conexao.execute(
            """INSERT INTO alunos
               (usuario_id, nome, sobrenome, idade)
               VALUES (?, ?, ?, ?)""",
            (usuario_id, "Felipe", "Prates", 16)
        )

        disciplinas = [
            ("Português", 8.5),
            ("Matemática", 9.0),
            ("História", 8.0),
            ("Geografia", 8.5),
            ("Física", 7.5),
            ("Química", 8.0),
            ("Biologia", 9.0),
            ("Inglês", 9.5),
            ("Educação Física", 10.0),
            ("Sociologia", 8.5)
        ]

        conexao.executemany(
            """INSERT INTO notas (usuario_id, disciplina, nota)
               VALUES (?, ?, ?)""",
            [(usuario_id, disciplina, nota) for disciplina, nota in disciplinas]
        )

    conexao.commit()
    conexao.close()


def login_obrigatorio(funcao):
    @wraps(funcao)
    def verificar_login(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return funcao(*args, **kwargs)

    return verificar_login


def pode_votar(idade):
    return idade >= 18


def pode_dirigir(idade):
    return idade >= 18


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sobre")
def sobre():
    jogos = [
        {
            "titulo": "GTA V",
            "imagem": "https://upload.wikimedia.org/wikipedia/en/a/a5/Grand_Theft_Auto_V.png",
            "descricao": "Um jogo de mundo aberto que mistura ação, liberdade e histórias memoráveis em Los Santos."
        },
        {
            "titulo": "Red Dead Redemption 2",
            "imagem": "https://upload.wikimedia.org/wikipedia/en/4/44/Red_Dead_Redemption_II.jpg",
            "descricao": "Uma experiência de narrativa profunda, exploração incrível e um cenário belíssimo."
        },
        {
            "titulo": "The Last of Us Part I",
            "imagem": "https://cdn.akamai.steamstatic.com/steam/apps/1888930/library_600x900.jpg",
            "descricao": "Um jogo emocionante e intenso, com uma história marcante."
        },
        {
            "titulo": "God of War",
            "imagem": "https://cdn.akamai.steamstatic.com/steam/apps/1593500/library_600x900.jpg",
            "descricao": "Uma jornada com desafios e desenvolvimento forte dos personagens."
        },
        {
            "titulo": "Marvel's Spider-Man",
            "imagem": "https://cdn.akamai.steamstatic.com/steam/apps/1817070/library_600x900.jpg",
            "descricao": "Ação, exploração urbana e uma ótima sensação de ser o Homem-Aranha."
        }
    ]

    filmes = [
        {
            "titulo": "Cidade de Deus",
            "imagem": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=900&q=80",
            "descricao": "Um filme intenso e marcante."
        },
        {
            "titulo": "Velozes e Furiosos 9",
            "imagem": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=900&q=80",
            "descricao": "Ação, velocidade e emoção."
        }
    ]

    series = [
        {
            "titulo": "Impuros",
            "imagem": "https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?auto=format&fit=crop&w=900&q=80",
            "descricao": "Uma série envolvente, com drama e tensão."
        },
        {
            "titulo": "Tropa de Elite",
            "imagem": "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?auto=format&fit=crop&w=900&q=80",
            "descricao": "Um clássico intenso e realista."
        }
    ]

    return render_template("sobre.html", jogos=jogos, filmes=filmes, series=series)


@app.route("/login", methods=["GET", "POST"])
def login():
    erro = ""

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        conexao = conectar()
        dados = conexao.execute(
            "SELECT * FROM usuarios WHERE usuario = ?",
            (usuario,)
        ).fetchone()
        conexao.close()

        if dados and check_password_hash(dados["senha"], senha):
            session["usuario_id"] = dados["id"]
            session["usuario"] = dados["usuario"]
            return redirect(url_for("boletim"))

        erro = "Usuário ou senha inválidos."

    return render_template("login.html", erro=erro)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/boletim")
@login_obrigatorio
def boletim():
    usuario_id = session["usuario_id"]

    conexao = conectar()
    notas = conexao.execute(
        """SELECT disciplina, nota
           FROM notas
           WHERE usuario_id = ?
           ORDER BY id""",
        (usuario_id,)
    ).fetchall()
    conexao.close()

    valores = [nota["nota"] for nota in notas]
    media = sum(valores) / len(valores) if valores else 0
    situacao = "Aprovado" if media >= 6 else "Recuperação"

    return render_template(
        "boletim.html",
        notas=notas,
        media=media,
        situacao=situacao
    )


@app.route("/informacoes")
@login_obrigatorio
def informacoes():
    usuario_id = session["usuario_id"]

    conexao = conectar()
    aluno = conexao.execute(
        """SELECT nome, sobrenome, idade
           FROM alunos
           WHERE usuario_id = ?""",
        (usuario_id,)
    ).fetchone()
    conexao.close()

    return render_template(
        "informacoes.html",
        aluno=aluno,
        pode_votar=pode_votar(aluno["idade"]),
        pode_dirigir=pode_dirigir(aluno["idade"])
    )


iniciar_banco()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
