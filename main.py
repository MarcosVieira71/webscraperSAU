from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import date
import os
from dotenv import load_dotenv
import time

load_dotenv()

path = 'https://sau.puc-rio.br/WebLoginPucOnline/Default.aspx?sessao=VmluY3Vsbz1BJlNpc3RMb2dpbj1QVUNPTkxJTkVfQUxVTk8mQXBwTG9naW49TE9HSU4mRnVuY0xvZ2luPUxPR0lOJlNpc3RNZW51PVBVQ09OTElORV9BTFVOTyZBcHBNZW51PU1FTlUmRnVuY01lbnU9TUVOVQ__'
print(os.getenv('USER'), os.getenv('PASSWORD'))

html_ctx: dict = {
    'input_user': 'input#txtLogin',
    'input_password': 'input#txtSenha',
    'submit_btn': 'input[type=submit]',
    'username': '#lblNomeUsuario',
}

def make_login(hide_browser: bool):
    try:
        with sync_playwright() as p:
            bw = p.chromium.launch(headless=hide_browser, slow_mo=50)
            pg = bw.new_page()
            pg.goto(path)
            pg.fill(html_ctx['input_user'], '#')
            pg.fill(html_ctx['input_password'], '*')
            pg.click(html_ctx['submit_btn'])
            error_login = pg.is_visible('div.pnlAlertModalTipoErro')
            print(error_login)
            if error_login:
                print("Erro no login.\n")
            else:
                html = pg.inner_html(html_ctx['username'])
                print(html)
                save_log(html)

            sau_goto(pg, 'Horários e salas de aula')
    except Exception as e:
        print("Error: ", e)

def save_log(text: str):
    with open(f'log_{date.today()}.txt', 'w') as f:
        f.write(text)
    f.close()
    print("Sucess writing log.\n")

def sau_goto(pg, menu_item: str):
    if menu_item == 'Horários e salas de aula':
        pg.get_by_text("Horários e salas de aula").click()
        content = pg.inner_html('#pnlQuadHora')
        elemento = getClasses(content)
        for k,v in elemento.items():
            print(f"{k}: {v}, {len(v)}")

def extractClass(container):
    class_elements = container.find_all('div', class_=['quadroHora_dcp2Hora', 'quadroHora_dcpHora'])
    classes_info = []
    for div in class_elements:
        class_texts = [span.get_text() for span in div.find_all('span', class_='descricao_caixa')]
        classes_info.append(class_texts)
    return classes_info


def getClasses(contentHorarios):
    soup = BeautifulSoup(contentHorarios, 'html.parser')
    days = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]
    classesPerDay = {}
    for dia in days:
        container_id = f"pnlQuadHora_Container_{dia}"
        container = soup.find(id=container_id)
        classesPerDay[dia] = extractClass(container)
    return classesPerDay
 

make_login(hide_browser=True)