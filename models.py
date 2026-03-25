import psycopg2
import pandas as pd
from decimal import Decimal
import os

from config import Config

def get_connection():
    try:
        params = Config.get_connection_params()
        print("Parâmetros de conexão:", params)  # Log para verificar os parâmetros de conexão
        
        conn = psycopg2.connect(
            host=params['host'],
            database=params['database'],
            user=params['user'],
            password=params['password'],
            port=params['port']
        )
        print("Conexão com PostgreSQL estabelecida com sucesso.")
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise

def create_gastos(numero_onibus, tipo_de_frota, litros, motorista, numero_de_controle, quem_abasteceu, quilometragem, hora, media, data_gasto, tipo_abastecimento):
    print(f"Inserindo dados: {numero_onibus}, {litros}, {motorista}, {numero_de_controle}, {quem_abasteceu}, {quilometragem}, {hora}, {data_gasto}")

    if not all([numero_onibus, tipo_de_frota, litros, motorista, quem_abasteceu, quilometragem, hora, data_gasto]) or (tipo_abastecimento != "externo" and not numero_de_controle):
        raise ValueError("Todos os campos são obrigatórios, exceto o Número de Controle para abastecimento externo.")

    try:
        litros = Decimal(litros)
        quilometragem = float(quilometragem)
    except ValueError:
        raise ValueError("Litros e quilometragem devem ser numéricos.")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO gastos (NumeroOnibus, Tipo_de_Frota, Litros, Motorista, Numero_de_controle, quem_abasteceu, quilometragem, hora, media, Data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                       (numero_onibus, tipo_de_frota, litros, motorista, numero_de_controle, quem_abasteceu, quilometragem, hora, media, data_gasto))
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar gastos: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def get_combustivel_disponivel():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT quantidade FROM combustivel")
        quantidade = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"Quantidade de combustível obtida: {quantidade}")  # Log da quantidade obtida
        return quantidade
    except Exception as e:
        print(f"Erro ao obter quantidade de combustível: {str(e)}")  # Log do erro
        raise

def atualizar_combustivel(quantidade):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE combustivel SET quantidade = %s", (quantidade,))
    conn.commit()
    cursor.close()
    conn.close()

def get_gastos(numero_onibus=None, start_date=None, end_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM gastos WHERE 1=1"
    params = []

    if numero_onibus:
        query += " AND NumeroOnibus = %s"
        params.append(numero_onibus)
    
    if start_date:
        query += " AND Data >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND Data <= %s"
        params.append(end_date)

    try:
        cursor.execute(query, tuple(params))
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        gastos_df = pd.DataFrame(data, columns=columns)
        print("Dados obtidos com sucesso:", gastos_df)
        return gastos_df
    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
    
    return gastos_df

def print_table_structure():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'gastos'")
    structure = cursor.fetchall()
    print("Estrutura da tabela Gastos:")
    for column in structure:
        print(column)

    cursor.execute("SELECT * FROM gastos")
    data = cursor.fetchall()
    print("Dados na tabela Gastos:")
    for row in data:
        print(row)

    cursor.close()
    conn.close()

def get_gastos_por_mes_ano(mes, ano):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gastos WHERE EXTRACT(MONTH FROM Data) = %s AND EXTRACT(YEAR FROM Data) = %s", (mes, ano))
    gastos = cursor.fetchall()
    cursor.close()
    conn.close()
    return gastos

def update_gastos(id, numero_onibus, litros, motorista):
    if not all([numero_onibus, litros, motorista]):
        raise ValueError("Todos os campos são obrigatórios.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE gastos SET NumeroOnibus=%s, Litros=%s, Motorista=%s WHERE Id=%s", (numero_onibus, litros, motorista, id))
    conn.commit()
    cursor.close()
    conn.close()

import os

def run_migration_script():
    migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'alter_tables.sql')
    with open(migration_file, 'r') as file:
        sql_script = file.read()

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql_script)
        conn.commit()
        print("Migração aplicada com sucesso.")
    except Exception as e:
        print(f"Erro ao aplicar migração: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print_table_structure()
