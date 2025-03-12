import requests
import concurrent.futures
import time

def enviar_requisicao(i, url):
    try:
        inicio = time.time()
        resposta = requests.get(url)
        tempo = time.time() - inicio
        return i, resposta.status_code, tempo
    except Exception as e:
        return i, None, None

def teste_de_carga(url, total_requisicoes=50, num_concorrentes=10):
    resultados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concorrentes) as executor:
        futuras = [executor.submit(enviar_requisicao, i, url) for i in range(total_requisicoes)]
        for futura in concurrent.futures.as_completed(futuras):
            indice, status, tempo = futura.result()
            resultados.append((indice, status, tempo))
            if status:
                print(f"Requisição {indice}: Status {status}, Tempo {tempo:.2f}s")
            else:
                print(f"Requisição {indice}: Falha ao conectar.")
    return resultados

if __name__ == "__main__":
    # Altere a URL abaixo para o endpoint da sua API
    url_teste = "http://seu-servidor.com/teste/"
    total_requisicoes = 50       # Total de requisições a serem enviadas
    num_concorrentes = 10        # Número de requisições concorrentes

    print(f"Iniciando teste de carga para {url_teste}")
    teste_de_carga(url_teste, total_requisicoes, num_concorrentes)
    print("Teste concluído.")
