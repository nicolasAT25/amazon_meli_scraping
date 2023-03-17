import pandas as pd
import webbrowser
import requests
import bs4
from IPython.display import display

def open_link(*args):
    for arg in args:
        try:
            if isinstance(arg, pd.DataFrame):
                df = arg
        except Exception as e:
            print("Error:",e)
        if isinstance(arg, str):
            try:
                links = df[df['Articulo']==arg]['Link']
                for link in links:webbrowser.open(link)
            except Exception as e:
                print("Error:",e)

        elif isinstance(arg, int) or isinstance(arg,float):
            try:
                webbrowser.open(df.loc[arg, 'Link'])
            except Exception as e:
                print("Error:",e)

        elif not isinstance(arg, pd.DataFrame) and not isinstance(arg, str) and not isinstance(arg, int) and not isinstance(arg,float):
            print(f"You passed an expected argument ({arg}): {type(arg)}")

def load_html_search_one_page():
    search = input('Insert your search:')
    url = 'https://listado.mercadolibre.com.mx/{}#D[A:{}]'.format(search.replace(' ','-'), search.replace(' ','%'))
    request = requests.get(url)
    print(f'Response status code: {request.status_code}')
    content = request.text
    soup = bs4.BeautifulSoup(content, 'html.parser') # HTML document

    print(f'***************{soup.title.text}***************')

    brands = []
    products = []
    prices = []
    links = []

    tag_filter_page = soup.find_all("div", {"class":"ui-search-result__content-wrapper shops__result-content-wrapper"})
    for tag in tag_filter_page:
        products.append(tag.find("h2").text)
        prices.append(tag.find(class_="price-tag-fraction").text)
        links.append(tag.find("a")["href"])
        brands.append(tag.find(class_="ui-search-item__brand-discoverability ui-search-item__group__element shops__items-group-details").text)

    data = {}
    data["Brand"] = brands
    data['Product'] = products
    data['Price'] = prices
    data["Link"] = links

    df = pd.DataFrame(data = data)
    df = df.drop_duplicates(ignore_index=True)
    df['Brand'] = df['Brand'].apply(lambda x: "-" if x == '' else x)
    df['Price'] = df['Price'].apply(lambda x: x.replace(",",""))
    df['Price'] = df['Price'].astype(int)
    print('Total products retrieved: {}'.format(df.shape[0]))
    display(df.head())

    return df

def load_html_search():
    search = input('Insert your search:')
    url = 'https://listado.mercadolibre.com.mx/{}#D[A:{}]'.format(search.replace(' ','-'), search)
    request = requests.get(url)
    print(f'Response status code: {request.status_code}')
    content = request.text
    soup = bs4.BeautifulSoup(content, 'html.parser') # HTML document

    total_pages = int(soup.find_all("div", {"class":"ui-search-pagination shops__pagination-content"})[0].find(class_="andes-pagination__page-count").text.replace("de ",""))
    current_page = soup.find_all("div", {"class":"ui-search-pagination shops__pagination-content"})[0].find("li").text # See actual page
    print(f'***************{soup.title.text}***************')
    print('Total pages: {}'.format(total_pages))
    print('Current page: {}\n\n'.format(current_page))

    brands = []
    products = []
    prices = []
    links = []

    for page in range(1,total_pages+1):
        url_page = f'https://listado.mercadolibre.com.mx/belleza-cuidado-personal/cuidado-cabello/crema-peinar/crema-para-peinar-rizos_Desde_{(page*50)+1}_NoIndex_True'
        request_page = requests.get(url_page)
        content_page = request_page.text
        soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
        tag_filter_page = soup_page.find_all("div", {"class":"ui-search-result__content-wrapper shops__result-content-wrapper"})

        for tag in tag_filter_page:
            products.append(tag.find("h2").text)
            prices.append(tag.find(class_="price-tag-fraction").text)
            links.append(tag.find("a")["href"])
            brands.append(tag.find(class_="ui-search-item__brand-discoverability ui-search-item__group__element shops__items-group-details").text)

    data = {}
    data["Brand"] = brands
    data['Articulo'] = products
    data['Price'] = prices
    data["Link"] = links

    df = pd.DataFrame(data = data)
    df = df.drop_duplicates(ignore_index=True)
    df['Brand'] = df['Brand'].apply(lambda x: "-" if x == '' else x)
    df['Price'] = df['Price'].apply(lambda x: x.replace(",",""))
    df['Price'] = df['Price'].astype(int)
    print('Total products retrieved: {}'.format(df.shape[0]))
    display(df.head())

    return df

def quartile_prices(df):
    try:
        describe = df['Price'].describe().to_frame()
        df_25 = df[df['Price'] <= describe.loc['25%'][0]].reset_index(drop=True)
        df_25_50 = df[(df['Price'] > describe.loc['25%'][0]) & (df['Price'] <= describe.loc['50%'][0])].reset_index(drop=True)
        df_50 = df[df['Price'] > describe.loc['50%'][0]].reset_index(drop=True)
    except Exception as e:
        print("Error:",e)

    return df_25, df_25_50, df_50, describe