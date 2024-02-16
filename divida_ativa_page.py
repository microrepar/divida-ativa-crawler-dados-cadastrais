#!/usr/bin/env python
# coding: utf-8
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import Config


def get_element_by_xpath(driver, xpath, max_wait=10):
    try:
        element = WebDriverWait(driver, max_wait).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        return element
    except:
        return None


def get_divida_ativa_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option('prefs', {
        'download.default_directory': 'C:/Users/codigo100cera/Downloads/divida ativa/parcelamento por data de emissão',
        'download.prompt_for_download': True,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True
    })

    driver = webdriver.Chrome( 
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )

    driver.get(Config.URL)

    username_field = get_element_by_xpath(driver, '//input[@name="username"]', max_wait=20)
    username_field.send_keys(Config.USUARIO)

    password_field = get_element_by_xpath(driver, '//input[@name="password"]', max_wait=20)
    password_field.send_keys(Config.SENHA)

    btn_entrar = get_element_by_xpath(driver, '//input[@type="image"]', max_wait=20)
    btn_entrar.click()

    link_divida_ativa = get_element_by_xpath(driver, '//a[contains(text(), "Dívida Ativa")]', max_wait=20)
    link_divida_ativa.click()

    link_outros_servicos = get_element_by_xpath(driver, '//b[contains(text(), "- Outros")]//ancestor::a', max_wait=20)
    link_outros_servicos.click()

    return driver


def registrar_arquivo_nao_encontrado(nome_arquivo):
    # Caminho para o arquivo de log
    log_path = Config.DIR_DESTINO / '.log'

    # Cria o diretório se ele não existir
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Obtém a data e hora atual
    data_hora_atual = datetime.datetime.now()

    # Formata a mensagem com o nome do arquivo e a data/hora
    mensagem = f" Data e Hora: {data_hora_atual} - Arquivo não encontrado: {nome_arquivo}\n"

    # Abre o arquivo de log em modo de apêndice (append) e escreve a mensagem
    with log_path.open('a') as arquivo_log:
        arquivo_log.write(mensagem)
