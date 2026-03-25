import os
from flask import Blueprint, request, jsonify, render_template, send_file, current_app
from models import create_gastos, get_gastos as fetch_gastos, get_combustivel_disponivel, atualizar_combustivel, get_connection
import datetime
import pandas as pd
import io
import psycopg2
from twilio.rest import Client
from decimal import Decimal
import time
import traceback

gastos_bp = Blueprint('gastos', __name__)
# Registro do blueprint movido para o app.py

# Configurações de conexão com o PostgreSQL
conn_str = {
    'host': os.getenv('DB_SERVER'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT')
}
 

client = Client(account_sid, auth_token)

import threading
from datetime import datetime, timedelta

# Variáveis para controle de envio de mensagens usando dicionário com timestamps
aviso_enviado = {
    7500: None,
    5000: None,
    2500: None
}
lock = threading.Lock()

def enviar_mensagem(mensagem):
    try:
        client.messages.create(
            to=to_number,
            from_=twilio_number,
            body=mensagem
        )
    except Exception as e:
        print(f"Erro ao enviar mensagem: {str(e)}")  # Log do erro

from models import get_combustivel_disponivel

def obter_quantidade_combustivel():
    return get_combustivel_disponivel()

@gastos_bp.route('/gastos', methods=['GET', 'POST'])  # Corrigido aqui
def add_gastos():
    try:
        data = request.get_json()
        if not data:
            current_app.logger.error("Dados não fornecidos no formato JSON")
            return jsonify({
                'error': 'Dados não fornecidos',
                'message': 'Por favor, forneça todos os dados necessários no formato JSON'
            }), 400

        current_app.logger.debug(f"Dados recebidos: {data}")

        numero_onibus = data.get('numeroOnibus')
        litros = data.get('litros')
        motorista = data.get('motorista')
        numero_de_controle = data.get('numeroControle')
        quem_abasteceu = data.get('quemAbasteceu')
        quilometragem = data.get('quilometragem')
        hora = data.get('hora')
        data_gasto = data.get('data')
        tipo_de_frota = data.get('tipoDeFrota')  # Adicionando o tipo de frota
        tipo_abastecimento = data.get('tipoAbastecimento')  # Adicionando o tipo de abastecimento

        print(f"Valores recebidos: NumeroOnibus={numero_onibus}, Litros={litros}, Motorista={motorista}, NumeroControle={numero_de_controle}, QuemAbasteceu={quem_abasteceu}, Quilometragem={quilometragem}, Hora={hora}, Data={data_gasto}, TipoFrota={tipo_de_frota}")

        # Validação rigorosa dos dados
        if not all([numero_onibus, litros, motorista, quem_abasteceu, quilometragem, hora, data_gasto, tipo_de_frota]):
            current_app.logger.error("Campos obrigatórios ausentes")
            return jsonify({'error': 'Todos os campos obrigatórios devem ser preenchidos.'}), 400
        if tipo_abastecimento != "externo" and not numero_de_controle:
            current_app.logger.error("Número de Controle obrigatório para abastecimento interno")
            return jsonify({'error': 'Número de Controle é obrigatório para abastecimento interno.'}), 400

        try:
            litros = Decimal(litros)  # Convertendo litros para Decimal
            quilometragem = float(quilometragem)
            data_gasto = datetime.strptime(data_gasto, '%Y-%m-%d')
        except Exception:
            current_app.logger.error("Litros, quilometragem e data inválidos")
            return jsonify({'error': 'Litros, quilometragem e data devem ser válidos.'}), 400

        # Verificar a quantidade disponível na tabela Combustivel
        quantidade_disponivel = get_combustivel_disponivel()

        if litros > quantidade_disponivel:
            return jsonify({'error': 'Quantidade de litros abastecida excede a quantidade disponível.'}), 400

        # Lógica para descontar a quantidade de combustível
        if tipo_abastecimento == "interno":
            nova_quantidade = quantidade_disponivel - litros
            atualizar_combustivel(nova_quantidade)

        gastos_df = fetch_gastos()
        print(f"Gastos retornados: {gastos_df}")  # Log para verificar os dados retornados
        ultimo_registro = gastos_df[gastos_df['numeroonibus'] == numero_onibus].iloc[-1] if not gastos_df[gastos_df['numeroonibus'] == numero_onibus].empty else None

        print(f"Último registro: {ultimo_registro}")  # Log para verificar o último registro

        if ultimo_registro is not None:
            diferenca_km = float(quilometragem) - float(ultimo_registro['quilometragem'])
            media = diferenca_km / float(litros) if float(litros) > 0 else 0.0
        else:
            media = 0.0

        print(f"Inserindo dados: {numero_onibus}, {litros}, {motorista}, {numero_de_controle}, {quem_abasteceu}, {quilometragem}, {hora}, {media}, {data_gasto}")

        create_gastos(numero_onibus, tipo_de_frota, litros, motorista, numero_de_controle, quem_abasteceu, quilometragem, hora, media, data_gasto, tipo_abastecimento)  # Atualizando a chamada

        # Verificar a quantidade de combustível após o abastecimento
        quantidade_combustivel = obter_quantidade_combustivel()
        now = datetime.now()

        with lock:
            for limite in [2500, 5000, 7500]:
                enviado_em = aviso_enviado.get(limite)
                if quantidade_combustivel < limite and (enviado_em is None or now - enviado_em > timedelta(hours=1)):
                    mensagem = f"Atenção: A quantidade de combustível está em {quantidade_combustivel} litros. Verificado em {now.strftime('%Y-%m-%d %H:%M:%S')}."
                    enviar_mensagem(mensagem)
                    aviso_enviado[limite] = now

        return jsonify({'message': 'Gasto criado com sucesso'}), 201

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        current_app.logger.error(f"Erro ao processar a requisição: {str(e)}\n{tb}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500

@gastos_bp.route('/gastos/view', methods=['GET'])
def get_gastos_view():
    try:
        gastos = fetch_gastos()
        
        # Verifica se os dados foram retornados corretamente
        if gastos.empty:
            return jsonify({
                'error': 'Dados vazios',
                'message': 'Nenhum dado de gastos encontrado'
            }), 404

        # Mapear os nomes das colunas conforme retornado pelo banco
        gastos_list = []
        for index, gasto in gastos.iterrows():
            gasto_dict = {
                'id': int(gasto.get('id', 0)),
                'NumeroOnibus': str(gasto.get('numeroonibus', '')),
                'Litros': float(gasto.get('litros', 0)),
                'Motorista': str(gasto.get('motorista', '')),
                'Data': str(gasto.get('data', '')),
                'Hora': str(gasto.get('hora', '')),
                'Numero_de_controle': str(gasto.get('numero_de_controle', '')),
                'quem_abasteceu': str(gasto.get('quem_abasteceu', '')),
                'quilometragem': float(gasto.get('quilometragem', 0)),
                'media': float(gasto.get('media', 0)),
                'Tipo_de_Frota': str(gasto.get('tipo_de_frota', ''))
            }
            gastos_list.append(gasto_dict)

        # Obter números de ônibus únicos
        unique_bus_numbers = gastos['numeroonibus'].dropna().unique().tolist()

        return jsonify({
            'data': gastos_list,
            'unique_bus_numbers': unique_bus_numbers,
            'message': 'Dados obtidos com sucesso'
        }), 200

    except Exception as e:
        print(f"Erro ao obter gastos: {str(e)}")  # Log do erro
        return jsonify({
            'error': 'Erro ao obter gastos',
            'message': str(e)
        }), 500

@gastos_bp.route('/gastos/filtrar', methods=['GET'])
def filtrar_gastos():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    numero_onibus = request.args.get('numero_onibus')
    motorista = request.args.get('motorista')

    print(f"Filtrando gastos com os parâmetros: start_date={start_date}, end_date={end_date}, numero_onibus={numero_onibus}, motorista={motorista}")  # Log dos parâmetros

    try:
        conn = psycopg2.connect(**conn_str)
        cursor = conn.cursor()

        query = """SELECT 
            id, numeroonibus, tipo_de_frota, litros, motorista, 
            numero_de_controle, quem_abasteceu, quilometragem, 
            hora, media, data 
            FROM gastos WHERE 1=1"""
        params = []

        if start_date:
            query += " AND data >= %s"
            params.append(start_date)
            print(f"Data de início: {start_date}")  # Log da data de início
        if end_date:
            query += " AND data <= %s"
            params.append(end_date)
            print(f"Data de fim: {end_date}")  # Log da data de fim
        if numero_onibus:
            query += " AND numeroonibus = %s"
            params.append(numero_onibus)
        if motorista:
            query += " AND motorista ILIKE %s"
            params.append(f"%{motorista}%")

        print(f"Consulta SQL: {query}, Parâmetros: {params}")  # Log da consulta SQL
        print("Executando a consulta...")  # Log para indicar que a consulta está sendo executada

        cursor.execute(query, params)
        gastos = cursor.fetchall()

        print(f"Gastos retornados da consulta: {gastos}")  # Log dos gastos retornados

        gastos_list = []  # Lista para armazenar os gastos filtrados
        for gasto in gastos:
            gastos_list.append({
                'id': int(gasto[0]),
                'NumeroOnibus': str(gasto[1]),
                'Tipo_de_Frota': str(gasto[2]),
                'Litros': float(gasto[3]),
                'Motorista': str(gasto[4]),
                'Numero_de_controle': str(gasto[5]),
                'quem_abasteceu': str(gasto[6]),
                'quilometragem': float(gasto[7]),
                'Hora': str(gasto[8]),
                'media': float(gasto[9]),
                'Data': str(gasto[10])
            })

        print(f"Gastos filtrados: {gastos_list}")  # Log dos gastos filtrados
        conn.close()
        return jsonify(gastos_list)
    except Exception as e:
        print(f"Erro ao filtrar gastos: {str(e)}")  # Log do erro
        return jsonify({'error': 'Erro ao filtrar gastos', 'message': str(e)}), 500

@gastos_bp.route('/gastos/download', methods=['GET'])
def download_relatorio():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    numero_onibus = request.args.get('numero_onibus')
    motorista = request.args.get('motorista')

    # Filtrar os gastos com base nos parâmetros fornecidos
    query = """SELECT 
        id, numeroonibus, litros, motorista, data, hora, 
        numero_de_controle, quem_abasteceu, quilometragem, 
        media, tipo_de_frota 
        FROM gastos WHERE 1=1"""
    params = []

    if start_date:
        query += " AND data >= %s"
        params.append(start_date)
    if end_date:
        query += " AND data <= %s"
        params.append(end_date)
    if numero_onibus:
        query += " AND numeroonibus = %s"
        params.append(numero_onibus)
    if motorista:
        query += " AND motorista ILIKE %s"
        params.append(f"%{motorista}%")

    # Executar a consulta e gerar o relatório
    try:
        conn = psycopg2.connect(**conn_str)
        cursor = conn.cursor()
        cursor.execute(query, params)
        gastos = cursor.fetchall()
        
        # Verificar se há dados retornados
        if not gastos:
            return jsonify({'error': 'Nenhum dado encontrado para os filtros aplicados.'}), 404

    except Exception as e:
        tb = traceback.format_exc()
        print(f"Erro ao gerar relatório: {str(e)}\n{tb}")  # Log do erro detalhado
        return jsonify({'error': 'Erro ao gerar relatório', 'message': str(e), 'traceback': tb}), 500

    finally:
        cursor.close()
        conn.close()  # Fechar a conexão

    # Criar um DataFrame com os dados filtrados
    df = pd.DataFrame.from_records(gastos, columns=['id', 'numeroonibus', 'litros', 'motorista', 'data', 'hora', 'numero_de_controle', 'quem_abasteceu', 'quilometragem', 'media', 'tipo_de_frota'])  # Especificar as colunas desejadas

    # Converter colunas datetime para timezone-naive para evitar erro no Excel
    if 'data' in df.columns:
        df['data'] = pd.to_datetime(df['data'], errors='coerce').dt.tz_localize(None)
    if 'hora' in df.columns:
        df['hora'] = pd.to_datetime(df['hora'], errors='coerce').dt.tz_localize(None)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Gastos')
    output.seek(0)
    # Ajustar o nome do arquivo para incluir motorista, numero_onibus ou nome genérico
    if motorista and isinstance(motorista, str) and motorista.strip():
        safe_motorista = motorista.strip().replace(" ", "_")
        filename = f'gastos_relatorio_motorista_{safe_motorista}.xlsx'
    elif numero_onibus:
        filename = f'gastos_relatorio_onibus_{numero_onibus}.xlsx'
    else:
        filename = 'gastos_relatorio.xlsx'
    return send_file(output, as_attachment=True, download_name=filename)  # Enviar o arquivo Excel como anexo

@gastos_bp.route('/combustivel/disponivel', methods=['GET'])
def combustivel_disponivel():
    try:
        print("Tentando obter a quantidade de combustível...")  # Log de início
        # Verificar a conexão com o banco de dados
        conn = get_connection()
        if conn:
            quantidade = get_combustivel_disponivel()
            conn.close()  # Fechar a conexão após a verificação
            print(f"Quantidade de combustível obtida: {quantidade}")  # Log da quantidade obtida
            return jsonify({
                'quantidade': quantidade,
                'message': 'Quantidade de combustível obtida com sucesso'
            }), 200
        else:
            print("Falha na conexão com o banco de dados.")  # Log de falha
            return jsonify({'error': 'Falha na conexão com o banco de dados'}), 500
    except Exception as e:
        print(f"Erro ao obter quantidade de combustível: {str(e)}")  # Log do erro
        return jsonify({
            'error': 'Erro ao obter quantidade de combustível',
            'message': str(e)
        }), 500
# Nova rota para reabastecimento
@gastos_bp.route('/reabastecer', methods=['POST'])
def reabastecer():
    data = request.get_json()
    if not data or 'litros' not in data:
        return jsonify({'error': 'Dados não fornecidos ou campo "litros" ausente'}), 400
    
    litros = data['litros']
    
    # Atualizar a quantidade de combustível disponível
    quantidade_atual = get_combustivel_disponivel()
    nova_quantidade = quantidade_atual + Decimal(litros)  # Convertendo litros para Decimal
    atualizar_combustivel(nova_quantidade)
    
    return jsonify({'nova_quantidade': nova_quantidade}), 200

# Outras rotas e funções permanecem inalteradas...

@gastos_bp.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Backend está rodando corretamente'}), 200
