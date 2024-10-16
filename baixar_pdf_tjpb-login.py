import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import argparse
from bs4 import BeautifulSoup

def countdown(message, seconds=5):
    print(message)
    for i in range(seconds, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("Pronto!")

def esperar_download(download_path, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        arquivos = os.listdir(download_path)
        arquivos_pdf = [f for f in arquivos if f.endswith('.pdf')]
        arquivos_crdownload = [f for f in arquivos if f.endswith('.crdownload')]
        if arquivos_pdf:
            return arquivos_pdf[-1]
        if not arquivos_crdownload:
            time.sleep(1)
    return None

def salvar_e_exibir_html(driver, nome_arquivo):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    html_formatado = soup.prettify()
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(html_formatado)
    
    print(f"HTML salvo em {nome_arquivo}")
    print("Primeiros 1000 caracteres do HTML formatado:")
    print(html_formatado[:1000])
    print("...")

def verificar_e_fazer_login(driver):
    try:
        # Verifica se o campo de login está presente
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "login:username")))
        
        print("Tela de autenticação detectada. Realizando login...")
        
        # Preenche o campo de usuário
        campo_usuario = driver.find_element(By.ID, "login:username")
        campo_usuario.clear()
        campo_usuario.send_keys("00760032483")
        
        # Preenche o campo de senha
        campo_senha = driver.find_element(By.ID, "login:password")
        campo_senha.clear()
        senha = os.environ.get('SENHA_DO_USUARIO')
        if not senha:
            raise ValueError("A variável de ambiente SENHA_DO_USUARIO não está definida.")
        campo_senha.send_keys(senha)
        
        # Clica no botão de login
        botao_login = driver.find_element(By.ID, "login:loginBtn")
        botao_login.click()
        
        print("Login realizado com sucesso.")
        time.sleep(5)  # Espera para a página carregar após o login
        
        return True
    except TimeoutException:
        # Se não encontrar a tela de login, assume que já está logado
        return False
    except Exception as e:
        print(f"Erro ao tentar fazer login: {e}")
        return False

def baixar_pdf_tjpb(numero_processo, headless=False):
    print("Configurando o driver do Chrome...")
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    
    if headless:
        chrome_options.add_argument("--headless")
        print("Modo headless ativado.")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_path = os.path.join(script_dir, "processos-adm-baixados")
    os.makedirs(download_path, exist_ok=True)
    print(f"Diretório de download: {download_path}")

    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        countdown("Abrindo a página do ADMEletrônico TJPB...")
        driver.get("https://app.tjpb.jus.br/ADMEletronico/consultaPublica.seam")
        
        verificar_e_fazer_login(driver)
        
        salvar_e_exibir_html(driver, "pagina_inicial.html")
        
        countdown("Esperando a página carregar completamente...")
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "processoSearch:j_id59:processoId")))
            print("Página carregada com sucesso.")
        except Exception as e:
            print(f"Erro ao carregar a página: {e}")
            print("Tentando continuar mesmo assim...")

        countdown("Preenchendo o número do processo...")
        try:
            campo_processo = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "processoSearch:j_id59:processoId"))
            )
            campo_processo.clear()
            campo_processo.send_keys(numero_processo)
            print(f"Número do processo '{numero_processo}' preenchido.")
        except Exception as e:
            print(f"Erro ao preencher o número do processo: {e}")
            return

        countdown("Clicando no botão de pesquisa...")
        try:
            botao_pesquisa = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "processoSearch:search"))
            )
            botao_pesquisa.click()
            print("Botão de pesquisa clicado.")
        except Exception as e:
            print(f"Erro ao clicar no botão de pesquisa: {e}")
            return

        countdown("Aguardando os resultados da pesquisa...")
        time.sleep(5)  # Espera adicional para garantir que os resultados sejam carregados
        
        verificar_e_fazer_login(driver)  # Verifica novamente após a pesquisa
        
        salvar_e_exibir_html(driver, "resultados_pesquisa.html")
        
        countdown("Procurando a linha com 'Despacho' e 'DIESP - Despachar'...")
        try:
            linha = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//tr[contains(., 'Despacho') and contains(., 'DIESP - Despachar')]"))
            )
            
            print("Linha encontrada.")
            
            icone_pdf = linha.find_element(By.XPATH, ".//img[@src='/ADMEletronico/img/pdf.gif']")
            print("Ícone do PDF encontrado.")
            
            countdown("Tentando clicar no ícone para baixar o PDF...")
            icone_pdf.click()
            print(f"Solicitação de download do PDF iniciada para o processo {numero_processo}")
            
            time.sleep(5)  # Espera adicional após o clique
            
            verificar_e_fazer_login(driver)  # Verifica novamente após tentar baixar o PDF
            
            salvar_e_exibir_html(driver, "apos_clique_pdf.html")
            
            print("Aguardando o download do arquivo...")
            arquivo_baixado = esperar_download(download_path)
            
            if arquivo_baixado:
                print(f"Arquivo baixado com sucesso: {arquivo_baixado}")
                print(f"Caminho completo do arquivo: {os.path.join(download_path, arquivo_baixado)}")
            else:
                print("Tempo limite de download excedido. O arquivo pode não ter sido baixado.")
                print("Conteúdo atual da pasta de downloads:")
                print(os.listdir(download_path))
        
        except Exception as e:
            print(f"Erro ao processar os resultados da pesquisa: {e}")
            salvar_e_exibir_html(driver, "erro_processamento.html")

    finally:
        if not headless:
            input("Pressione Enter para fechar o navegador e finalizar o script...")
        driver.quit()
        print("Navegador fechado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Baixar PDF do TJPB")
    parser.add_argument("numero_processo", help="Número do processo para pesquisar")
    parser.add_argument("--headless", action="store_true", help="Executar em modo headless")
    args = parser.parse_args()

    baixar_pdf_tjpb(args.numero_processo, args.headless)