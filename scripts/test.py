import os
import time
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# função para encerrar processos do Chrome
def kill_chrome_processes():
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if 'chrome' in process.info['name'].lower():
            try:
                process.terminate()
            except Exception as e:
                print(f"##### Erro ao encerrar processo {process.info['pid']}: {e} #######")

# limpar os arquivos do cache do navegador
def clear_cache_directory(directory):
    if not os.path.exists(directory):
        print("##### Diretório de cache não encontrado. ######")
        return
    
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            try:
                os.remove(os.path.join(root, file))
            except Exception as e:
                print(f"##### Erro ao remover {file}: {e} #####")
        
        for dir in dirs:
            try:
                os.rmdir(os.path.join(root, dir))
            except Exception as e:
                print(f"###### Erro ao remover diretório {dir}: {e} ######")

# abrir url do monitor
def open_url(url):
    # configuração que remove a mensagem no navegador de que ele está sendo controlado por um software de automatização
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # configuração para ignorar verificação SSL
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-web-security")
    
    # configuração para ignorar contadores do chrome
    chrome_options.add_argument("--disable-background-timer-throttling")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """
    })
    
    driver.get(url)
    
    return driver

# inserir senha e nome do monitor nos inputs
def insert_texts(driver, password, monitor_name):
    while True:
        time.sleep(10)
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            if len(inputs) >= 2:
                inputs[0].send_keys(password)
                inputs[1].send_keys(monitor_name)

                buttons = driver.find_elements(By.TAG_NAME, "button")
                if len(buttons) >= 3:
                    buttons[2].click()
                    break  # sai do loop quando os dados forem inseridos

        except Exception as e:
            print(f"##### Erro ao inserir os textos: {e} #####")
            return False  
        
    return True 
        
# função principal para iniciar o script
def execute(cache_directory, url, password, monitor_name):
    # finaliza processos do Chrome antes de iniciar
    kill_chrome_processes()
    
    # limpar cache do navegador
    clear_cache_directory(cache_directory)
    
    driver = open_url(url)
    
    success = insert_texts(driver, password, monitor_name)
    
    if success:
        driver.fullscreen_window()
        print("##### Sistema iniciado com sucesso. Aguardando 24 horas... #####")
        time.sleep(86400)  # 24 horas
    else:
        print("##### Falha ao inserir os textos. Reiniciando... ######")
    
    driver.quit()
    
load_dotenv()

# colocar o diretório do cache do navegador    
cache_directory = os.getenv("TEST_CACHE_DIR")
url = os.getenv("MONITOR_URL")  
password = os.getenv("EME_PASSWORD")  
monitor_name = os.getenv("EME_NAME")   

while True:
    execute(cache_directory, url, password, monitor_name)
    print("##### Reiniciando o processo... #####")
    time.sleep(5)