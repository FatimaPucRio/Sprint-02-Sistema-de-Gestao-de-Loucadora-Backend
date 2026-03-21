from datetime import date, datetime
from functools import wraps
import logging
import sqlite3
import webbrowser
from threading import Timer
from typing import Tuple

from flask import Flask, request, jsonify, Blueprint, redirect
from flasgger import Swagger
from flask_cors import CORS
from sqlite3 import IntegrityError

from db_config import get_conexao_db, DATABASE, inicializar_db
from utils import registrar_cliente, busca_filme_tmdb

# --- Configuração de Logging ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5001/apidocs")

def gerenciar_conexao_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = get_conexao_db()
        conn.row_factory = sqlite3.Row
        try:
            result = func(conn, *args, **kwargs)
            status_check = result[1] if isinstance(result, tuple) else 200
            if status_check in [200, 201, 204]:
                conn.commit()
            return result
        except IntegrityError:
            conn.rollback()
            return jsonify({"erro": "Recurso já existe ou viola restrições (CPF duplicado)."}), 409
        except Exception as e:
            conn.rollback()
            return jsonify({"erro": f"Erro inesperado: {str(e)}"}), 500
        finally:
            conn.close()
    return wrapper

def valida_idade(data_nascimento_str: str) -> Tuple[str, int]:
    try:
        data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Data inválida. Use YYYY-MM-DD.")
    hoje = date.today()
    idade = hoje.year - data_nascimento.year - (
        (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day)
    )
    if idade < 18:
        raise ValueError("Cliente deve ser maior de 18 anos.")
    return data_nascimento_str, idade

app = Flask(__name__)
CORS(app)

clientes_bp = Blueprint('clientes_bp', __name__, url_prefix='/clientes')
filmes_bp = Blueprint('filmes_bp', __name__, url_prefix='/filmes')

@app.route('/')
def inicio():
    return redirect('/apidocs')

# === CLIENTES ===

@clientes_bp.route('/', methods=['POST'])
def cadastra_cliente():
    """
    Cadastra um novo cliente
    ---
    tags:
      - Clientes
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              nome:
                type: string
              cpf:
                type: string
              data_nascimento:
                type: string
              email:
                type: string
              telefone:
                type: string
    responses:
      201:
        description: Cliente cadastrado
      400:
        description: Erro de validação
      409:
        description: CPF duplicado
    """
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON não enviado"}), 400

    try:
        valida_idade(dados.get('data_nascimento'))
        resultado, status = registrar_cliente(
            dados.get('nome'),
            dados.get('cpf'),
            dados.get('email', ''),
            dados.get('telefone', ''),
            dados.get('data_nascimento')
        )
        return jsonify(resultado), status
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

@clientes_bp.route('/', methods=['GET'])
@gerenciar_conexao_db
def lista_clientes(conn: sqlite3.Connection):
    """
    Lista todos os clientes
    ---
    tags:
      - Clientes
    responses:
      200:
        description: Lista de clientes
    """
    clientes = conn.execute("SELECT * FROM clientes").fetchall()
    return jsonify([dict(c) for c in clientes]), 200

@clientes_bp.route('/<int:id>', methods=['PUT'])
@gerenciar_conexao_db
def altera_cliente(conn: sqlite3.Connection, id: int):
    """
    Atualiza cliente
    ---
    tags:
      - Clientes
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              nome:
                type: string
              email:
                type: string
              telefone:
                type: string
              data_nascimento:
                type: string
    responses:
      200:
        description: Atualizado
      404:
        description: Não encontrado
    """
    dados = request.get_json(silent=True)

    try:
        valida_idade(dados.get('data_nascimento'))
        cursor = conn.execute("""
            UPDATE clientes
            SET nome=?, email=?, telefone=?, data_nascimento=?
            WHERE id=?
        """, (dados['nome'], dados['email'], dados['telefone'], dados['data_nascimento'], id))

        if cursor.rowcount == 0:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        return jsonify({"mensagem": "Cliente atualizado com sucesso"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@clientes_bp.route('/<int:id>', methods=['DELETE'])
@gerenciar_conexao_db
def deleta_cliente(conn: sqlite3.Connection, id: int):
    """
    Remove cliente
    ---
    tags:
      - Clientes
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: integer
    responses:
      204:
        description: Deletado
      404:
        description: Não encontrado
    """
    cursor = conn.execute("DELETE FROM clientes WHERE id = ?", (id,))
    if cursor.rowcount == 0:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    return '', 204

# === FILMES ===

@filmes_bp.route('/busca_externa', methods=['GET'])
def busca_filme_externa():
    """
    Busca filme externo
    ---
    tags:
      - Filmes
    parameters:
      - name: titulo
        in: query
        required: true
        schema:
          type: string
    responses:
      200:
        description: Filme encontrado
    """
    titulo = request.args.get('titulo')

    if not titulo:
        return jsonify({"erro": "Título é obrigatório."}), 400

    resultado = busca_filme_tmdb(titulo)
    return jsonify(resultado), 200

# --- FINAL ---
app.register_blueprint(clientes_bp)
app.register_blueprint(filmes_bp)

app.config['SWAGGER'] = {
    'title': 'API Sistema de Gestão de Locadora',
    'uiversion': 3,
    'openapi': '3.0.2'
}

swagger = Swagger(app)

if __name__ == '__main__':
    try:
        inicializar_db()
    except Exception as e:
        logger.error(f"Erro ao inicializar DB: {e}")

    logger.info("Servidor iniciado na porta 5000 (Docker 5001)")
    Timer(1.5, abrir_navegador).start()
    app.run(debug=True, host='0.0.0.0', port=5000)