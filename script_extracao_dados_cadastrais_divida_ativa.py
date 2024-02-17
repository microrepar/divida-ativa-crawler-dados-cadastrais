import time
from pathlib import Path
from config import Config

import pandas as pd
from selenium.webdriver.common.by import By

from divida_ativa_page import get_divida_ativa_driver, get_element_by_xpath

# ### File Locations
in_file_estoque = Path.cwd() / "data" / "raw" / "2024-01-11 Lista estoque dívida acima de 50000.xlsx"
in_file_parcelas = Path.cwd() / "data" / "raw" / "2024-01-11 Lista de parcelas acima de 500 a partir de 01-11-2023.xlsx"

in_file_log = Path.cwd() / "data" / "raw" / "log.csv"

summary_file_imobiliario = Path.cwd() / "data" / "processed" / f"dados_cadastrais_imobiliario.csv"
summary_file_mobiliario = Path.cwd() / "data" / "processed" / f"dados_cadastrais_mobiliario.csv"

dtypes={
    'IdCadastro': 'string',
    'inscricao': 'string',
}

df_estoque = pd.read_excel(in_file_estoque, dtype=dtypes)
df_parcelas = pd.read_excel(in_file_parcelas, dtype=dtypes)

df_memo = pd.read_csv(in_file_log, dtype=dtypes)

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
    inscricoes_prontas = df_memo['inscricao'].tolist()
    contador = 0

    for name, df in [('ESTOQUE', df_estoque), ('PARCELAS', df_parcelas)]:
        contador += 1
        if contador % 100 == 0: print(f'>>>>>>>qtde. inscrições>>>>>>> {contador:0>4}')

        lista_cadastros = df['IdCadastro'].unique()
        print(f'>>>>>>>>>>>{name}>>>>>>>>>>', len(lista_cadastros))
        
        for cadastro in lista_cadastros:
            tipo, inscricao = str(cadastro[:-11].replace('0', '')), str(cadastro[-11:])

            # se ja existe a incricao do tipo imobiliario no arquivo de log
            # vai para o proximo da lista
            if inscricao in inscricoes_prontas: 
                # print('>>>>>>>NEXT>>>>>>', inscricao, ' - ', tipo)
                continue

            if tipo == '1':
                dados_cadastrais = get_dados_cadastrais_imobiliario(driver, tipo, inscricao)
                
                if dados_cadastrais is None:
                    # se houve algum problema na extracao adiciona a inscricao                 
                    # com o status de "error" no log do tipo=1 imobiliario
                    df_memo.loc[len(df_memo)] = [tipo, inscricao, 'error']
                    continue
                else:                    
                    df_imobiliario.loc[len(df_imobiliario)] = dados_cadastrais

            if tipo == '2':
                inscricao_tipo2 = str(int(inscricao))
                
                dados_cadastrais_list = get_dados_cadastrais_mobiliario(driver, tipo, inscricao_tipo2)

                if dados_cadastrais_list is None:
                    # se houve algum problema na extracao adiciona a inscricao 
                    # com o status de "error" no log do tipo=2 mobiliario
                    df_memo.loc[len(df_memo)] = [tipo, inscricao, 'error']
                    continue
                else:                
                    for dados_cadastrais in dados_cadastrais_list:
                        df_mobiliario.loc[len(df_mobiliario)] = dados_cadastrais
                    
            # adiciona no log a inscricao completou a extracao dos dados cadastrais
            df_memo.loc[len(df_memo)] = [tipo, inscricao, 'ok']
            
except Exception as error:
    print('>>>>>ERROR>>>>>', tipo, ' | ', inscricao)

    df_imobiliario.to_csv(summary_file_imobiliario, index=False)
    df_mobiliario.to_csv(summary_file_mobiliario, index=False)
    df_memo.to_csv(in_file_log, index=False)
    
    raise error



df_imobiliario.to_csv(summary_file_imobiliario, index=False)
df_mobiliario.to_csv(summary_file_mobiliario, index=False)
df_memo.to_csv(in_file_log, index=False)

print('***EXTRAÇÃO REALIZADA COM SUCESSO***')