from flask import Flask, render_template, jsonify, request
from flask_cors import CORS  # Importando CORS
from routes import gastos_bp  # Ajuste na importação
import datetime
from models import get_combustivel_disponivel  # Importando a função
from dotenv import load_dotenv
import os
import logging  # Importando o módulo de logging
from flask import jsonify
from werkzeug.exceptions import HTTPException
import threading
import webbrowser

# Configuração de logging
logging.basicConfig(filename='flask.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:%(message)s')

load_dotenv()  # Carrega as variáveis do arquivo .env

print("DB_SERVER:", os.getenv("DB_SERVER"))  # Debug para verificar variável de ambiente

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

from flask_cors import CORS

CORS(app, resources={r"/*": {"origins": "*"}})  # Aplicando CORS para todas as rotas

app.register_blueprint(gastos_bp, url_prefix='/api')  # Registro do blueprint com prefixo /api

from flask import render_template

@app.route('/')
def serve_index():
    return render_template('index.html')

# Handler global para erros HTTP e não HTTP
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        response = e.get_response()
        response.data = jsonify({
            "error": e.name,
            "description": e.description,
            "code": e.code
        }).data
        response.content_type = "application/json"
        app.logger.error(f"HTTPException: {e.name} - {e.description}")
        return response
    else:
        app.logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal Server Error",
            "description": "Ocorreu um erro interno no servidor."
        }), 500

@app.route('/gastos')
def serve_gastos():
    return render_template('gastos.html')

@app.route('/teste')
def teste():
    return "Rota de teste funcionando!"

@app.route('/combustivel/disponivel', methods=['GET'])
def combustivel_disponivel():
    try:
        quantidade = get_combustivel_disponivel()
        return jsonify({"quantidade": quantidade})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-cors', methods=['GET'])
def test_cors():
    response = jsonify({"message": "CORS está funcionando"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def open_browser(port):
    webbrowser.open_new(f"http://localhost:{port}/")

if __name__ == "__main__":
    from waitress import serve
    port = int(os.getenv("PORT", 8000))
    # Removendo abertura automática do navegador para rodar como serviço
    # threading.Timer(1.5, open_browser, args=(port,)).start()
    serve(app, host='0.0.0.0', port=port)
