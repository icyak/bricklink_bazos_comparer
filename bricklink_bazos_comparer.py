import re
import pandas as pd
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup

XPATH_PRICE = '//*[@id="_idItemTableForS"]/table/tbody/tr[2]/td[7]/text()'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
    'x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}
SEARCH_FOR_THIS = 'lego+star+wars'
EXCLUDE = '-ps4+-xbox+-ninjago+-chima+-play+-dvd+-knihy+-nintendo+-Napodobenina+-PC'


def render_js(url):
    """Function providing renreding of js on url."""
    session = HTMLSession()
    response_store = session.get(url)
    response_store.html.render(timeout=20)
    response_store.close()
    session.close()
    return response_store

def extract_data(target_url,xpath):
    """Function extracting price, when not present provide 0.00."""
    rendered_page_response = render_js(target_url)
    data = rendered_page_response.html.xpath(xpath)
    if len(data) == 0:
        data = "[EUR, 0.00]"
    return data

def list_to_string(s):
    """Function providing list->string conversion"""
    str1 = ""
    for ele in s:
        str1 += ele
    return str1

def list_to_int(input_list):
    """Function providing list->float->int conversion."""
    list_to_str = list_to_string(input_list)
    try:
        list_str = float(list_to_str)
    except ValueError:
        list_str = float(0.0)
    list_str = int(list_str)
    return list_str

def bazos_bricklink_download_and_compare():
    """Function downloading first page of specific bazos URL, and search sets on bricklink"""
    baseurl = f'https://www.bazos.sk/search.php?hledat={SEARCH_FOR_THIS}+{EXCLUDE}&rubriky=www&hlokalita=&humkreis=25&cenaod=&cenado=&kitx=ano'
    output_list = []
    response = requests.get(baseurl, headers=HEADERS, timeout=3)
    soup = BeautifulSoup(response.content, 'lxml')
    product_list = soup.find_all('div', class_='inzeraty inzeratyflex')
    for item in product_list:
        bazos_name = item.find('h2', class_='nadpis').text.strip()
        bazos_price_int = list_to_int(re.findall(r'\b\d+\b',(item.find\
            ('div', class_='inzeratycena').text.strip())))
        bazos_date_added = item.find('span', class_='velikost10').text.strip()
        bazos_views = item.find('div', class_='inzeratyview').text.strip()
        bazos_set_id_int = list_to_string(re.findall(r'\b\d+\b', bazos_name))
        bl_url = f"https://www.bricklink.com/v2/search.page?q={bazos_set_id_int}&type=S&reg=-1&tab=S#T=S"
        bl_price_int = list_to_int(re.findall(r"(?:\d*\.*\d+)",list_to_string\
            (extract_data(bl_url,XPATH_PRICE)[0].split())))
        out = {
                'ID' : bazos_set_id_int,
                'DESCRIPTION': bazos_name,
                'DATE': bazos_date_added,
                'PRICE': bazos_price_int,
                'BL_PRICE:': bl_price_int,
                'DIFF' : bazos_price_int - bl_price_int,
                'VIEWS': bazos_views,       
                #'URL': bl_url
            }
        print(out)
        output_list.append(out)
    pd.set_option('display.max_colwidth', None)
    dataframe = pd.DataFrame(output_list)
    print(130 * '*')
    print()
    print(dataframe)
    print()
    print(130 * '*')

bazos_bricklink_download_and_compare()
