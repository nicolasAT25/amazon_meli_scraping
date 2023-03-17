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
            #print(f"A pandas DataFrame expected. You passed: {type(arg)}")
        if isinstance(arg, str):
            try:
                links = df[df['Product']==arg]['Link']
                for link in links:webbrowser.open(link)
            except Exception as e:
                print("Error:",e)
                #print(f"Verify your entry is actually correct: {e}")
        elif isinstance(arg, int) or isinstance(arg,float):
            try:
                webbrowser.open(df.loc[arg, 'Link'])
            except Exception as e:
                print("Error:",e)
                #print(f"There is some issue with your request: {e}")
        elif not isinstance(arg, pd.DataFrame) and not isinstance(arg, str) and not isinstance(arg, int) and not isinstance(arg,float):
            print(f"You passed an expected argument ({arg}): {type(arg)}")

def load_html_search_one_page():
    search = input('Insert your search:').replace(" ","+").lower()
    url = f'https://www.amazon.com.mx/s?k={search}&sprefix=play%2Caps%2C245&ref=nb_sb_ss_ts-doa-p_1_4'
    headers = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36","Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Upgrade-Insecure-Requests": "1",}
    request = requests.get(url, headers=headers)
    print(f'Response status code: {request.status_code}')
    content = request.text
    soup = bs4.BeautifulSoup(content, 'html.parser') # HTML document

    print(f'***************{soup.title.text}***************')

    products = []
    prices = []
    stars = []

    tag_filter_page = soup.find_all("div", {"class":"a-section a-spacing-small puis-padding-left-small puis-padding-right-small"})

    for tag in tag_filter_page:
            try:
                products.append(tag.find("span", class_="a-size-base-plus").text)
            except Exception as e:
                #print(f'Tag not found ({tag}) - {e}')
                products.append('-')

            try:
                prices.append(int(tag.find("span", class_='a-price-whole').text.strip(".").replace(",","")))
            except Exception as e:
                #print(f'Tag not found ({tag}) - {e}')
                prices.append(0)

            try:
                stars.append(float(tag.find("div", class_="a-row a-size-small").find(class_="a-size-base").text))
            except Exception as e:
                #print(f'Tag not found ({tag}) - {e}')
                stars.append(0.0)

    data = {}
    data['Product'] = products
    data['Price'] = prices
    data["Stars"] = stars

    df = pd.DataFrame(data = data)
    df = df.drop_duplicates(ignore_index=True)
    print('Total products retrieved: {}'.format(df.shape[0]))
    display(df.head())

    return df

def load_html_search():
    search = input('Insert your search:').replace(" ","+").lower()
    url = f'https://www.amazon.com.mx/s?k={search}&sprefix=play%2Caps%2C245&ref=nb_sb_ss_ts-doa-p_1_4'
    headers = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36","Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Upgrade-Insecure-Requests": "1",}
    request = requests.get(url, headers=headers)
    print(f'Response status code: {request.status_code}')
    content = request.text
    soup = bs4.BeautifulSoup(content, 'html.parser') # HTML document

    total_pages = int(soup.find_all("span", {"class":"s-pagination-item s-pagination-disabled"})[0].text)
    print(f'***************{soup.title.text}***************')
    print('Total pages: {}'.format(total_pages))

    products = []
    prices = []
    stars = []
    links = []

    for page in range(1,total_pages+1): # ÅMÅŽÕÑ
        if page == 1:
            url_page = f'https://www.amazon.com.mx/s?k={search}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss'
            request_page = requests.get(url_page, headers=headers)
            content_page = request_page.text
            soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
            tag_filter_page = soup_page.find_all("div", {"class":"a-section a-spacing-small puis-padding-left-small puis-padding-right-small"})
        else:
            url_page = f'https://www.amazon.com.mx/s?k={search}&page={page}&qid=1678315624&sprefix=play%2Caps%2C245&ref=sr_pg_{page-1}'
            request_page = requests.get(url_page, headers=headers)
            content_page = request_page.text
            soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
            tag_filter_page = soup_page.find_all("div", {"class":"a-section a-spacing-small puis-padding-left-small puis-padding-right-small"})

        print('Scraping page {}/{}'.format(soup_page.find_all("span", {"class":"s-pagination-item s-pagination-selected"})[0].text, total_pages))

        for tag in tag_filter_page:
            try:
                products.append(tag.find("span", class_="a-size-base-plus").text)
            except:
                products.append('-')

            try:
                prices.append(int(tag.find("span", class_='a-price-whole').text.strip(".").replace(",","")))
            except:
                prices.append(0)

            try:
                stars.append(float(tag.find("div", class_="a-row a-size-small").find(class_="a-size-base").text))
            except:
                stars.append(0.0)

            try:
                links.append('https://www.amazon.com.mx/'+tag.find("a", class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")["href"])
            except:
                links.append("-")

    data = {}
    data['Product'] = products
    data['Price'] = prices
    data["Stars"] = stars
    data["Link"] = links

    df = pd.DataFrame(data = data)
    df = df.drop_duplicates(ignore_index=True)
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