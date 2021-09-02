from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import requests
import time
import csv
import re
from selenium.webdriver.support import expected_conditions as EC
global url_all

url_all = ['https://yandex.ru/uslugi/2-saint-petersburg/category/yuristyi--3141',
           'https://yandex.ru/uslugi/2-saint-petersburg/category/yuristyi/arbitrazhnyie-sporyi--3174',
           'https://yandex.ru/uslugi/2-saint-petersburg/category/yuristyi/yuridicheskoe-soprovozhdenie-sdelok--3 542',
           'https://yandex.ru/uslugi/2-saint-petersburg/category/yuristyi/yuridicheskie-dokumentyi--3515',
           'http://yandex.ru/uslugi/2-saint-petersburg/category/yuristyi/proverka-dokumentov-i-dogovorov--3405',
           'https://yandex.ru/uslugi/2-saint-petersburg/category/yuristyi/predstavitelstvo-v-sude--3394']

headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36 OPR/66.0.3515.60'}

options = webdriver.chrome.options.Options()

driver = webdriver.Chrome(chrome_options=options)
driver.implicitly_wait(10)

def get_urllist(url, ses, headers):
    soup = get_html(url, ses, headers)
    box = soup.find('div', {'class':'Loader'}).find_all('div', {'class':'WorkerCard Card'})
    catalog = []

    for a in box:
        catalog.append('https://yandex.ru' + a.find('a', {'class':'Link WorkerCard-Title'}).get('href'))

    return catalog

def get_html(url, ses, headers):
    response = ses.get(url, headers=headers)
    soup = bs(response.text, 'lxml')

    return soup

def get_data(url, ses, headers, main_url):

    while True:
        driver.get(url)
        source = driver.page_source
        sup = bs(source, 'lxml')
        try:
            all = sup.find('div', {'class':'WorkerSpecializationsList'}).find_all('div', {'class':'Collapse'})
            break
        except:
            time.sleep(1)

    for a in all:
        button = driver.find_element_by_class_name('WorkerSpecializationsList').find_element_by_id(a.get('id'))

        driver.execute_script("arguments[0].scrollIntoView();", button)
        while True:
            try:
                button.click()
                break
            except:
                driver.execute_script("arguments[0].scrollIntoView();", button)
                time.sleep(1)
        more = driver.find_element_by_class_name('WorkerSpecializationsList').find_element_by_id(a.get('id')).find_elements_by_class_name('Text')
        if more[-1].text.split(' ')[0] == 'Ещё':
            try:
                driver.execute_script("arguments[0].scrollIntoView();", more[-1])
                more[-1].click()
                more = driver.find_element_by_class_name('WorkerSpecializationsList').find_element_by_id(a.get('id')).find_elements_by_class_name('Text')

            except:
                print("SERIUOS ERRROR")

        for z in more:
                if z.text == 'Читать ещё':
                    while True:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView();", z)
                            z.click()
                            break
                        except:
                            time.sleep(2)
                            cross = driver.find_element_by_class_name('modal').find_element_by_class_name('Icon')
                            driver.execute_script("arguments[0].scrollIntoView();", cross)
                            cross.click()
                            print('error')


    source = driver.page_source

    page = bs(source, 'lxml')
    all_uslugi = page.find('div', {'class':'WorkerSpecializationsList'}).find_all('div', {'class':'Collapse Collapse_visible Card SpecializationCardCollapse'})

    for a in all_uslugi:
        name_usl = a.find('b').text
        jobs = a.find_all('div', {'class':'ServiceCard-Main'})
        for z in jobs:
            try:
                price_job = z.find('b', {'class':'Text Text_line_m Text_size_m ServiceCard-Price'}).text.split('₽')[0]
            except:
                price_job = 'По договоренности'

            name_job = z.find('b', {'class':'Text Text_line_m Text_size_m'}).text
            try:
                opis = z.find('span', {'class':'Text Text_line_m Text_size_m Text_formatted Text_hyphens TextBlock ServiceCard-Descr Gap Gap_top_xs'}).text
                opis = re.sub("^\s+|\n|\r|\s+$", '', opis)
            except:
                opis = ''

            print(name_usl + '->' + name_job + ' ' + opis + ' ' + price_job)

            data = {'name_usl': name_usl,
                     'name_job': name_job,
                     'opis': opis,
                     'price': price_job}

            write_csv(data, url_all, main_url)

def write_csv(data, url_all, main_url):
    if main_url == url_all[0]:
        filename = 'Все юристы.csv'
    elif main_url == url_all[1]:
        filename = 'Арбитражные споры.csv'
    elif main_url == url_all[2]:
        filename = 'Юридическое сопровождение сделок.csv'
    elif main_url == url_all[3]:
        filename = 'Юридические документы.csv'
    elif main_url == url_all[4]:
        filename = 'Проверка документов и договоров.csv'
    else:
        filename = 'Представительство в суде.csv'

    with open(filename, 'a',  encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow((data['name_usl'],
                         data['name_job'],
                         data['price'],
                         data['opis']))

def main(headers, url_all):
    pagecurrent=0
    ses = requests.Session()

    for url in url_all:
        while True:

            data = get_html(url, ses, headers)
            urls = get_urllist(url, ses, headers)
            for a in urls:
                print(a)
                get_data(a, ses, headers, url)
            try:
                url = 'https://yandex.ru' + data.find('div', {'class':'Pager Serp-Pager'}).find('a', {'class':'Link Pager-TextItem', 'rel':'next'}).get('href')
            except:
                break

main(headers, url_all)
