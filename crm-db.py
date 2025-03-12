import os
import random
from dotenv import load_dotenv
import psycopg2
from psycopg2 import pool
import concurrent.futures
import time

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações de conexão com o PostgreSQL usando variáveis de ambiente
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432))
}

# Inicializa o pool de conexões
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, **DB_CONFIG)
    if connection_pool:
        print("Pool de conexões criado com sucesso")
except Exception as error:
    print("Erro ao criar pool de conexões:", error)
    exit(1)

def executar_evento_api(indice):
    """
    Simula um fluxo de operação da API:
    1. Consulta o número de registros na tabela.
    2. Insere um novo evento.
    3. Atualiza o evento inserido.
    Retorna o tempo total de execução.
    """
    conn = None
    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()
        inicio = time.time()
        
        # 1. Consulta a contagem atual de registros
        cur.execute("SELECT count(*) FROM simulated_events;")
        count_before = cur.fetchone()[0]
        
        # 2. Insere um novo evento
        cur.execute(
            "INSERT INTO simulated_events (event, created_at) VALUES (%s, NOW()) RETURNING id;",
            ("evento simulado",)
        )
        new_id = cur.fetchone()[0]
        
        # 3. Atualiza o evento inserido (simulando um processamento adicional)
        cur.execute(
            "UPDATE simulated_events SET event = %s WHERE id = %s;",
            ("evento atualizado", new_id)
        )
        
        conn.commit()
        tempo = time.time() - inicio
        cur.close()
        connection_pool.putconn(conn)
        print(f"Evento {indice}: Count Antes: {count_before}, Novo ID: {new_id}, Tempo: {tempo:.3f}s")
        return indice, new_id, tempo
    except Exception as e:
        if conn:
            connection_pool.putconn(conn)
        print(f"Evento {indice}: Erro: {e}")
        return indice, None, None

def teste_carga_eventos(total_eventos=1000, num_concorrentes=50):
    resultados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concorrentes) as executor:
        futuras = [
            executor.submit(executar_evento_api, i) for i in range(total_eventos)
        ]
        for futura in concurrent.futures.as_completed(futuras):
            resultados.append(futura.result())
    return resultados

if __name__ == "__main__":
    total_eventos = 1000      # Total de eventos (fluxos) a serem simulados
    num_concorrentes = 50     # Número de operações concorrentes

    print("Iniciando teste de carga simulando eventos da API...")
    resultados = teste_carga_eventos(total_eventos, num_concorrentes)
    print("Teste concluído.")

    # Fechar o pool de conexões
    if connection_pool:
        connection_pool.closeall()
