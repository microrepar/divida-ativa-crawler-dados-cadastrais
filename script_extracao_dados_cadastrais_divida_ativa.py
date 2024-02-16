import time
from pathlib import Path
from config import Config

import pandas as pd
from selenium.webdriver.common.by import By

from divida_ativa_page import get_divida_ativa_driver, get_element_by_xpath

# ### File Locations
in_file_estoque = Path.cwd() / "data" / "raw" / "2024-01-11 Lista estoque dívida acima de 50000.xlsx"
in_file_parcelas = Path.cwd() / "data" / "raw" / "2024-01-11 Lista de parcelas acima de 500 a partir de 01-11-2023.xlsx"
in_file_memo_im = Path.cwd() / "data" / "raw" / "memo_imobiliario.csv"
in_file_memo_mo = Path.cwd() / "data" / "raw" / "memo_mobiliario.csv"
summary_file_imobiliario = Path.cwd() / "data" / "processed" / f"dados_cadastrais_imobiliario.csv"
summary_file_mobiliario = Path.cwd() / "data" / "processed" / f"dados_cadastrais_mobiliario.csv"

dtypes={
    'IdCadastro': 'string'
}

df_estoque = pd.read_excel(in_file_estoque, dtype=dtypes)
df_parcelas = pd.read_excel(in_file_parcelas, dtype=dtypes)

df_memo_im = pd.read_csv(in_file_memo_im)
df_memo_mo = pd.read_csv(in_file_memo_mo)

driver = get_divida_ativa_driver()


def get_dados_cadastrais_imobiliario(driver, tipo, inscricao):
    url_imobiliario = (Config.URL_IMOB)
    
    for _ in range(2):
        driver.get(url_imobiliario)        
        campo_inscricao = get_element_by_xpath(driver, '//input[@name="ic"]')
        campo_inscricao.clear()
        campo_inscricao.send_keys(inscricao)

        campo_digito = get_element_by_xpath(driver, '//input[@name="digito"]')
        campo_digito.clear()
        campo_digito.send_keys('0')

        campo_documento = get_element_by_xpath(driver, '//input[@name="docto"]')
        campo_documento.clear()
        campo_documento.send_keys('0')

        btn_continuar = get_element_by_xpath(driver, '//input[@type="image"]')
        btn_continuar.click()

        btn_consultar_dados = get_element_by_xpath(
            driver, '//img[@src="/ps_image/btw.php?cont=Consultar D.A."]', max_wait=3)
        if btn_consultar_dados is None:
            inscricao = int(inscricao)        
            continue            
        btn_consultar_dados.click()

        btn_dados_cadastrais = get_element_by_xpath(driver, '//input[@value="Dados Cadastrais"]', 3)        
        if btn_dados_cadastrais is not None:
            btn_dados_cadastrais.click()
            break

        inscricao = int(inscricao)        
    else:
        return None

    dado_inscricao = None
    dado_responsavel = None
    dado_endereco_completo = None
    dado_cpf_cnpj = None
    dado_local_imovel = None
    dado_endereco_correio = None

    get_element_by_xpath(driver, '//input[@value="Dados Cadastrais"]//ancestor::table[@class="titulo"]//tr//')    
    table_header = driver.find_elements(By.XPATH, '//input[@value="Dados Cadastrais"]//ancestor::table[@class="titulo"]//td')
    dado_inscricao, dado_responsavel = [d.text for d in table_header][0].split(' - ')

    table_body = driver.find_elements(By.XPATH, '//input[@value="Dados Cadastrais"]//ancestor::table[@class="titulo"]//following::table[1]//tr')
    for i, row in enumerate(table_body):
        dados = row.find_elements(By.TAG_NAME, 'td')
        if i == 0:
            _, dado_endereco_completo, _, dado_cpf_cnpj = [d.text for d in dados]
        if i == 1:
            _, dado_local_imovel = [d.text for d in dados]
            
        if i == 2:
            dado_local_imovel += f' - {row.text}'

        if i == 3:
            _, dado_endereco_correio = [d.text for d in dados]

        if i == 4:
            dado_endereco_correio += f' - {row.text}'

    return (inscricao, tipo, dado_inscricao, dado_responsavel, dado_endereco_completo, 
            dado_cpf_cnpj, dado_local_imovel, dado_endereco_correio)


def get_dados_cadastrais_mobiliario(driver, tipo, inscricao):
    url_mobiliario = (Config.URL_MOB)
    
    for _ in range(2):
        driver.get(url_mobiliario)
        campo_cadastro = get_element_by_xpath(driver, '//input[@name="cadm"]')
        campo_cadastro.clear()
        campo_cadastro.send_keys(inscricao)

        campo_digito = get_element_by_xpath(driver, '//input[@name="digito"]')
        campo_digito.clear()
        campo_digito.send_keys('0')

        campo_documento = get_element_by_xpath(driver, '//input[@name="docto"]')
        campo_documento.clear()
        campo_documento.send_keys('0')

        btn_continuar = get_element_by_xpath(driver, '//input[@type="image"]')
        btn_continuar.click()

        btn_consultar_dados = get_element_by_xpath(driver, '//img[@src="/ps_image/btw.php?cont=Consultar D.A."]', 3)
        if btn_consultar_dados is None:
            inscricao = int(inscricao)
            continue
        btn_consultar_dados.click()

        btn_dados_cadastrais = get_element_by_xpath(driver, '//input[@value="Dados Cadastrais"]', 3)
        if btn_dados_cadastrais is None:
            inscricao = int(inscricao)
            continue            
        btn_dados_cadastrais.click()
        break
    else:
        return None

    dado_inscricao = None
    dado_razao_social = None
    dado_endereco = None
    dado_documento = None
    dado_nome_fantasia = None
    dado_estabelecimento = None
    dado_tipo_tributo = None

    table_header = driver.find_elements(By.XPATH, '//input[@value="Dados Cadastrais"]//ancestor::table[@class="titulo"]//td')
    dado_inscricao, dado_razao_social = [d.text.strip() for d in table_header][0].split(' - ')

    table_body = driver.find_elements(By.XPATH, '//input[@value="Dados Cadastrais"]//ancestor::table[@class="titulo"]//following::table[1]//tr')
    dado_endereco, dado_documento = ' '.join([d.text for d in table_body][0].split()[:-2]), [d.text for d in table_body][0].split()[-1]
    dado_endereco += f' - {[d.text for d in table_body][1]}'
    dado_nome_fantasia = [d.text for d in table_body][2].split(':')[-1]
    dado_estabelecimento = [d.text for d in table_body][3].split(':')[-1]
    dado_tipo_tributo = [d.text for d in table_body][4].split(':')[-1]

    table_body = driver.find_elements(By.XPATH, '//input[@value="Dados Cadastrais"]//ancestor::table[@class="titulo"]//following::table[2]//tr')
    socio_list = []
    for i, row in enumerate(table_body):
        dados = row.find_elements(By.TAG_NAME, 'td')
        if i == 0:
            if 'C.P.F' not in row.text.upper():
                socio = [None, None, None, None]
                socio_list.append(socio)
                break
            continue
        socio = [d.text for d in dados]
        socio_list.append(socio)

    list_dados = []
    for socio in socio_list:
        dados = [
            inscricao,
            tipo,
            dado_inscricao,
            dado_razao_social,
            dado_endereco,
            dado_documento,
            dado_nome_fantasia,
            dado_estabelecimento,
            dado_tipo_tributo,
        ] + socio

        list_dados.append(tuple(dados))
    
    return list_dados


try:
    df_imobiliario = pd.read_csv(summary_file_imobiliario)
    df_mobiliario = pd.read_csv(summary_file_mobiliario)
except FileNotFoundError:
    df_imobiliario = pd.DataFrame(columns=['inscr', 'tipo', 'inscricao', 'responsavel', 'endereco_completo', 
                                        'documento', 'local_imovel', 'endereco_correio'])

    df_mobiliario = pd.DataFrame(columns=['inscr', 'tipo', 'inscricao', 'razao_social', 'endereco', 'documento', 
                                        'nome_fantasia', 'estabelecimento', 'tipo_tributo', 
                                        'nome_socio', 'cpf_socio', 'rg_socio', 'data_socio'])

try:
    tipo = inscricao = None

    for cadastro in df_parcelas['IdCadastro']:
        tipo, inscricao = cadastro[:-11].replace('0', ''), cadastro[-11:]

        if tipo == '1':
            if df_memo_im['inscricao'].isin([inscricao]).any(): continue
            
            dados_cadastrais = get_dados_cadastrais_imobiliario(driver, tipo, inscricao)
            if dados_cadastrais is None:
                df_memo_im.loc[len(df_memo_im)] = [tipo, inscricao, 'error']
                continue
            df_imobiliario.loc[len(df_imobiliario)] = dados_cadastrais

            df_memo_im.loc[len(df_memo_im)] = [tipo, inscricao, 'ok']

        if tipo == '2':
            inscricao = inscricao[-5:]

            if df_memo_mo['inscricao'].isin([inscricao]).any(): continue
            
            dados_cadastrais_list = get_dados_cadastrais_mobiliario(driver, tipo, inscricao)
            if dados_cadastrais_list is None:
                df_memo_mo.loc[len(df_memo_mo)] = [tipo, inscricao, 'error']
                continue
            
            for dados_cadastrais in dados_cadastrais_list:
                df_mobiliario.loc[len(df_mobiliario)] = dados_cadastrais
            df_memo_mo.loc[len(df_memo_mo)] = [tipo, inscricao, 'ok']
        
        df_imobiliario.to_csv(summary_file_imobiliario, index=False)
        df_mobiliario.to_csv(summary_file_mobiliario, index=False)
        df_memo_im.to_csv(in_file_memo_im, index=False)
        df_memo_mo.to_csv(in_file_memo_mo, index=False)


    for cadastro in df_estoque['IdCadastro']:
        tipo, inscricao = cadastro[:-11].replace('0', ''), cadastro[-11:]

        if tipo == '1':
            if df_memo_im['inscricao'].isin([inscricao]).any(): continue
            
            dados_cadastrais = get_dados_cadastrais_imobiliario(driver, tipo, inscricao)
            if dados_cadastrais is None:
                df_memo_im.loc[len(df_memo_im)] = [tipo, inscricao, 'error']
                continue
            df_imobiliario.loc[len(df_imobiliario)] = dados_cadastrais

            df_memo_im.loc[len(df_memo_im)] = [tipo, inscricao, 'ok']

        if tipo == '2':
            inscricao = inscricao[-5:]

            if df_memo_mo['inscricao'].isin([inscricao]).any(): continue
            
            dados_cadastrais_list = get_dados_cadastrais_mobiliario(driver, tipo, inscricao)
            if dados_cadastrais_list is None:
                df_memo_mo.loc[len(df_memo_mo)] = [tipo, inscricao, 'error']
                continue
            
            for dados_cadastrais in dados_cadastrais_list:
                df_mobiliario.loc[len(df_mobiliario)] = dados_cadastrais
            df_memo_mo.loc[len(df_memo_mo)] = [tipo, inscricao, 'ok']
        
        df_imobiliario.to_csv(summary_file_imobiliario, index=False)
        df_mobiliario.to_csv(summary_file_mobiliario, index=False)
        df_memo_im.to_csv(in_file_memo_im, index=False)
        df_memo_mo.to_csv(in_file_memo_mo, index=False)

except Exception as error:
    print('>>>>>ERROR>>>>>', tipo, ' | ', inscricao)
    raise error
