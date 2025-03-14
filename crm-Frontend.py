# load_test.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import concurrent.futures

def simular_usuario(url, id_usuario):
    # Configuração para executar o Chrome em modo headless
    opcoes = Options()
    opcoes.add_argument("--headless")
    
    # Certifique-se de que o chromedriver está no PATH ou informe o caminho correto
    driver = webdriver.Chrome(options=opcoes)
    inicio = time.time()
    
    try:
        driver.get(url)
        tempo_carregamento = time.time() - inicio
        print(f"Usuário {id_usuario} carregou a página em {tempo_carregamento:.2f} segundos.")
        return tempo_carregamento
    except Exception as e:
        print(f"Erro para o usuário {id_usuario}: {e}")
        return None
    finally:
        driver.quit()

def executar_teste_carga(url, quantidade_usuarios):
    resultados = []
    
    # Utiliza ThreadPoolExecutor para simular os acessos em paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=quantidade_usuarios) as executor:
        futures = [executor.submit(simular_usuario, url, i+1) for i in range(quantidade_usuarios)]
        for future in concurrent.futures.as_completed(futures):
            tempo = future.result()
            if tempo is not None:
                resultados.append(tempo)
    
    if resultados:
        media = sum(resultados) / len(resultados)
        print(f"\nTeste concluído com {len(resultados)} usuários.")
        print(f"Tempo médio de carregamento: {media:.2f} segundos.")
    else:
        print("Nenhum carregamento bem-sucedido.")

if __name__ == "__main__":
    import sys
    # Exemplo de uso: python load_test.py http://seusite.com 20
    url = sys.argv[1] if len(sys.argv) > 1 else "https://crm-frontend-8yaz.onrender.com/"
    quantidade_usuarios = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    executar_teste_carga(url, quantidade_usuarios)