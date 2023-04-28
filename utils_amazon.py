import pandas as pd
import re
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
    url = f'https://www.amazon.com.mx/s?k={search}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss'
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", 
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
    request = requests.get(url, headers=headers)
    content = request.text
    soup = bs4.BeautifulSoup(content, 'html.parser') # HTML document

    while soup.find_all("span", {"class":"s-pagination-item s-pagination-disabled"}).__len__() == 0:
        url = f'https://www.amazon.com.mx/s?k={search}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss'
        headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", 
        "Accept-Encoding": "gzip, deflate, br",
        "Upgrade-Insecure-Requests": "1", 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
        request = requests.get(url, headers=headers)
        content = request.text
        soup = bs4.BeautifulSoup(content, 'html.parser') # HTML document

    print(f'Response status code: {request.status_code}')
    total_pages = int(soup.find_all("span", class_="s-pagination-item s-pagination-disabled")[0].text)
    print(f'***************{soup.title.text}***************')
    print('Total pages: {}'.format(total_pages))

    products = []
    prices = []
    stars = []
    links = []  

    for page in range(1, total_pages+1): # ÅMÅŽÕÑ
        if page == 1:
            url_page = f'https://www.amazon.com.mx/s?k={search}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss'
            request_page = requests.get(url_page, headers=headers)
            content_page = request_page.text
            soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
            tag_filter_page = soup_page.find_all("div", {"class":"a-section a-spacing-small puis-padding-left-small puis-padding-right-small"})

            while soup_page.find_all("div", {"class":"a-section a-spacing-small puis-padding-left-small puis-padding-right-small"}).__len__() == 0: #soup.find_all("span", {"class":"s-pagination-item s-pagination-disabled"}).__len__() == 0:
                url_page = f'https://www.amazon.com.mx/s?k={search}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss'
                request_page = requests.get(url_page, headers=headers)
                content_page = request_page.text
                soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
                tag_filter_page = soup_page.find_all("div", {"class":"a-section a-spacing-small puis-padding-left-small puis-padding-right-small"})

        else:
            url_page = f'https://www.amazon.com.mx/s?k={search}&page={page}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&qid=1681248772&ref=sr_pg_{page}'
            request_page = requests.get(url_page, headers=headers)
            content_page = request_page.text
            soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
            tag_filter_page = soup_page.find_all("div", {"class":"a-section a-spacing-small puis-padding-left-small puis-padding-right-small"})

            while soup_page.find_all("div", {"class":"a-section a-spacing-small puis-padding-left-small puis-padding-right-small"}).__len__() == 0: #soup_page.find_all("span", {"class":"s-pagination-item s-pagination-disabled"}).__len__() == 0:
                url_page = f'https://www.amazon.com.mx/s?k={search}&page={page}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&qid=1681248772&ref=sr_pg_{page}'
                request_page = requests.get(url_page, headers=headers)
                content_page = request_page.text
                soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
                tag_filter_page = soup_page.find_all("div", {"class":"a-section a-spacing-small puis-padding-left-small puis-padding-right-small"})

        print('Scraping page {}/{}'.format(soup_page.find_all("span", class_="s-pagination-item s-pagination-selected")[0].text, total_pages))

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
                #stars.append(float(tag.find("div", class_="a-row a-size-small").find(class_="a-size-base").text))
                stars.append(float(re.match(r'\d.\d',tag.find('span',class_="a-icon-alt").text)[0]))
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

    display(df.head())

    #Test
    df = df.copy().head(10)
    print('Copy made!!!!!!!!!!!!!')
    print(df.shape)

    # Add ratings and comments to the DataFrame
    ratings = []
    comments = []

    for i in range(df.__len__()):
        link_prod = df.loc[i, 'Link']
        request_ = requests.get(link_prod, headers=headers)
        #print(f'Response status code: {request_.status_code}')
        content_ = request_.text
        soup_ = bs4.BeautifulSoup(content_, 'html.parser') # HTML document
        rating_comm_tag_filter = soup_.find(id="reviewsMedley")
        #print(type(rating_comm_tag_filter))

        while rating_comm_tag_filter is None: ## | rating_comm_tag_filter.__len__() == 0:
            link_prod = df.loc[i, 'Link']
            request_ = requests.get(link_prod, headers=headers)
            #print(f'Response status code: {request_.status_code}')
            content_ = request_.text
            soup_ = bs4.BeautifulSoup(content_, 'html.parser') # HTML document
            rating_comm_tag_filter = soup_.find(id="reviewsMedley")

        comments_prod = []

        if soup_.find(id="reviewsMedley").find("span", class_="a-size-base a-color-secondary") is None:
            ratings.append(0)
        else:    
            ratings.append(int(re.search(r'\d+', soup_.find(id="reviewsMedley").find("span", class_="a-size-base a-color-secondary").text.strip().replace(",",""))[0]))

        for comm in rating_comm_tag_filter.find_all('div', class_='a-row a-spacing-small review-data'):
            comments_prod.append(re.sub(r'\n.+', '', comm.find('span').text.strip()))
        comments.append(comments_prod)

    #print(ratings)
    #print(comments)

    df['Ratings'] = ratings
    df['Comments'] = comments

    print('Total products retrieved: {}'.format(df.shape[0]))
    display(df.head())
    
    if total_pages == 0 or total_pages is None:
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

        #Test
        #df = df.copy().head(10)
        #print('Copy made!!!!!!!!!!!!!')
        #print(df.shape)

        # Add ratings and comments to the DataFrame
        ratings = []
        comments = []

        for i in range(df.__len__()):
            link_prod = df.loc[i, 'Link']
            request_ = requests.get(link_prod, headers=headers)
            #print(f'Response status code: {request_.status_code}')
            content_ = request_.text
            soup_ = bs4.BeautifulSoup(content_, 'html.parser') # HTML document
            rating_comm_tag_filter = soup_.find(id="reviewsMedley")

            print(soup_.find(id="reviewsMedley"))

            comments_prod = []
            if (rating_comm_tag_filter is None):    #  | (rating_comm_tag_filter.__len__() == 0)
                ratings.append(0)
                comments.append('-')
            else: #(rating_comm_tag_filter.__len__() > 0) | (rating_comm_tag_filter is not None):
                ratings.append(int(re.search(r'\d+', soup_.find(id="reviewsMedley").find("span", class_="a-size-base a-color-secondary").text.strip().replace(",",""))[0]))
                for comm in rating_comm_tag_filter.find_all('div', class_='a-row a-spacing-small review-data'):
                    comments_prod.append(re.sub(r'\n.+', '', comm.find('span').text.strip()))
            comments.append(comments_prod)

        #print(ratings)
        #print(comments)

        df['Ratings'] = ratings
        df['Comments'] = comments

        print('Total products retrieved: {}'.format(df.shape[0]))
        display(df.head())

    return df

def quartile_prices(df):
    try:
        describe = df['Price'].describe().to_frame().round(2)
        df_25 = df[df['Price'] <= describe.loc['25%'][0]].reset_index(drop=True)
        df_25_50 = df[(df['Price'] > describe.loc['25%'][0]) & (df['Price'] <= describe.loc['50%'][0])].reset_index(drop=True)
        df_50_75 = df[(df['Price'] > describe.loc['50%'][0]) & (df['Price'] <= describe.loc['75%'][0])].reset_index(drop=True)
        df_75 = df[df['Price'] > describe.loc['75%'][0]].reset_index(drop=True)
    except Exception as e:
        print("Error:",e)

    return df_25, df_25_50, df_50_75, df_75, describe

# Work (backup)
'''def load_html_search_():
    search = input('Insert your search:').replace(" ","+").lower()
    url = f'https://www.amazon.com.mx/s?k={search}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss'
    headers = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36","Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Upgrade-Insecure-Requests": "1",}
    request = requests.get(url, headers=headers)
    content = request.text
    soup = bs4.BeautifulSoup(content, 'html.parser') # HTML document

    while soup.find_all("span", {"class":"s-pagination-item s-pagination-disabled"}).__len__() == 0:
        url = f'https://www.amazon.com.mx/s?k={search}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss'
        headers = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36","Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Upgrade-Insecure-Requests": "1",}
        request = requests.get(url, headers=headers)
        content = request.text
        soup = bs4.BeautifulSoup(content, 'html.parser') # HTML document

    print(f'Response status code: {request.status_code}')
    total_pages = int(soup.find_all("span", {"class":"s-pagination-item s-pagination-disabled"})[0].text)
    print(f'***************{soup.title.text}***************')
    print('Total pages: {}'.format(total_pages))

    products = []
    prices = []
    stars = []
    links = []

    for page in range(1,5): # ÅMÅŽÕÑ total_pages+1
        if page == 1:
            url_page = f'https://www.amazon.com.mx/s?k={search}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss'
            request_page = requests.get(url_page, headers=headers)
            content_page = request_page.text
            soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
            tag_filter_page = soup_page.find_all("div", {"class":"a-section a-spacing-small puis-padding-left-small puis-padding-right-small"})
            while soup_page.find_all("span", {"class":"s-pagination-item s-pagination-disabled"}).__len__() == 0:
                url_page = f'https://www.amazon.com.mx/s?k={search}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss'
                request_page = requests.get(url_page, headers=headers)
                content_page = request_page.text
                soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
                tag_filter_page = soup_page.find_all("div", {"class":"a-section a-spacing-small puis-padding-left-small puis-padding-right-small"})
        else:
            url_page = f'https://www.amazon.com.mx/s?k={search}&page={page}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&qid=1681248772&ref=sr_pg_{page}'
            request_page = requests.get(url_page, headers=headers)
            content_page = request_page.text
            soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
            tag_filter_page = soup_page.find_all("div", {"class":"a-section a-spacing-small puis-padding-left-small puis-padding-right-small"})
            while soup_page.find_all("span", {"class":"s-pagination-item s-pagination-disabled"}).__len__() == 0:
                url_page = f'https://www.amazon.com.mx/s?k={search}&page={page}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&qid=1681248772&ref=sr_pg_{page}'
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

    return df'''