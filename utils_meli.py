import pandas as pd
import re
import time
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

def load_html_search():
    search = input('Insert your search:')
    print(f'Keywords: {search.replace("-"," ")}')
    url = 'https://listado.mercadolibre.com.mx/{}#D[A:{}]'.format(search.replace(' ','-'), search)
    request = requests.get(url)
    content = request.text
    soup = bs4.BeautifulSoup(content, 'html.parser') # HTML document

    # brands = []
    products = []
    prices = []
    links = []

    pages_flag = soup.find_all("div", {"class":"ui-search-pagination shops__pagination-content"})


    if pages_flag.__len__() != 0:
        print(f'Response status code: {request.status_code}')
        total_pages = int(soup.find("div", class_="ui-search-pagination shops__pagination-content").find("li",class_="andes-pagination__page-count").text.replace("de ",""))
        print(f'***************{soup.title.text}***************')
        print('Total pages: {}'.format(total_pages))

        for page in range(1,total_pages+1):
            if page == 1:
                url_page = 'https://listado.mercadolibre.com.mx/{}_NoIndex_True'.format(search.replace(' ','-'))
                request_page = requests.get(url_page)
                content_page = request_page.text
                soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
                tag_filter_page = soup_page.find_all("div", {"class":"ui-search-result__content-wrapper shops__result-content-wrapper"})

                while soup_page.find_all("div", {"class":"ui-search-result__content-wrapper shops__result-content-wrapper"}).__len__() == 0:
                    url_page = 'https://listado.mercadolibre.com.mx/{}_NoIndex_True'.format(search.replace(' ','-'))
                    request_page = requests.get(url_page)
                    content_page = request_page.text
                    soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
                    tag_filter_page = soup_page.find_all("div", {"class":"ui-search-result__content-wrapper shops__result-content-wrapper"})

                # for tag in tag_filter_page:
                #     brands.append(tag.find(class_="ui-search-item__brand-discoverability ui-search-item__group__element shops__items-group-details").text)
                #     products.append(tag.find("h2").text)
                #     prices.append(tag.find(class_="price-tag-fraction").text)
                #     links.append(tag.find("a")["href"])

            else:
                url_page = 'https://listado.mercadolibre.com.mx/{}_Desde_{}_NoIndex_True'.format(search.replace(' ','-'),(page*50)+1-50)
                request_page = requests.get(url_page)
                content_page = request_page.text
                soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
                tag_filter_page = soup_page.find_all("div", {"class":"ui-search-result__content-wrapper shops__result-content-wrapper"})

                while soup_page.find_all("div", {"class":"ui-search-result__content-wrapper shops__result-content-wrapper"}).__len__() == 0:
                    url_page = 'https://listado.mercadolibre.com.mx/{}_Desde_{}_NoIndex_True'.format(search.replace(' ','-'),(page*50)+1-50)
                    request_page = requests.get(url_page)
                    content_page = request_page.text
                    soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
                    tag_filter_page = soup_page.find_all("div", {"class":"ui-search-result__content-wrapper shops__result-content-wrapper"}) 

                # for tag in tag_filter_page:
                #     products.append(tag.find("h2").text)
                #     prices.append(tag.find(class_="price-tag-fraction").text)
                #     links.append(tag.find("a")["href"])
                #     brands.append(tag.find(class_="ui-search-item__brand-discoverability ui-search-item__group__element shops__items-group-details").text)
        
            # current_page = soup.find_all("div", {"class":"ui-search-pagination shops__pagination-content"})[0].find("li").text # See actual page
            # print(soup.find("div", class_="ui-search-pagination shops__pagination-content").find("li",class_="andes-pagination__page-count").text)
            print('Scraping page {}/{}'.format(page,total_pages))

            for tag in tag_filter_page:
                # brands.append(tag.find(class_="ui-search-item__brand-discoverability ui-search-item__group__element shops__items-group-details").text)
                products.append(tag.find("h2").text)
                prices.append(tag.find("span",class_="andes-money-amount__fraction").text)
                # prices.append(tag.find(class_="price-tag-fraction").text)
                links.append(tag.find("a")["href"])

        data = {}
        # data["Brand"] = brands
        data['Product'] = products
        data['Price'] = prices
        data["Link"] = links

        df = pd.DataFrame(data = data)
        df = df.drop_duplicates(ignore_index=True)
        # df['Brand'] = df['Brand'].apply(lambda x: "-" if x == '' else x)
        df['Price'] = df['Price'].apply(lambda x: x.replace(",",""))
        df['Price'] = df['Price'].astype(int)

        print(df.shape)
        display(df.head(3))

        # Test
        df = df.copy().head(10)
        print('Copy made!')

        # Add score, ratings and comments to the DataFrame
        scores = []
        ratings = []
        comments = []

        for i in range(df.__len__()):
            link_prod = df.loc[i, 'Link']
            request_ = requests.get(link_prod)
            content_ = request_.text
            soup_ = bs4.BeautifulSoup(content_, 'html.parser') # HTML document
            score_rating_tag_filter = soup_.find('div', class_="ui-review-capability")#.find(class_="ui-review-capability__rating__average ui-review-capability__rating__average--desktop").text
            
            # print(f'Before: {type(score_rating_tag_filter)}')

            attemps = 0
            while score_rating_tag_filter is None and attemps < 101:
                link_prod = df.loc[i, 'Link']
                request_ = requests.get(link_prod)
                content_ = request_.text
                soup_ = bs4.BeautifulSoup(content_, 'html.parser') # HTML document
                score_rating_tag_filter = soup_.find('div', class_="ui-review-capability")
                attemps += 1

            # print(f'After: {type(score_rating_tag_filter)}')
            
            if score_rating_tag_filter is None:
                scores.append(0.0)
                ratings.append(0)
            else:
                scores.append(float(score_rating_tag_filter.find("p",class_="ui-review-capability__rating__average ui-review-capability__rating__average--desktop").text))
                ratings.append(int(re.match(r'\d+',score_rating_tag_filter.find(class_="ui-review-capability__rating__label").text)[0]))  #r'[0-9]+'

            # comments_tag_filter = soup_.find('div', {"class":"infinite-scroll-component "})
            comments_tag_filter = soup_.find('section', {"class":"ui-review-capability-main"})
            # comments_tag_filter = soup_.find_all('article', {"class":"ui-review-capability-comments__comment"})x

            comments_prod = []
            if comments_tag_filter is None:
                comments_prod.append('-')
            else:
                for comm in comments_tag_filter.find_all('p', class_="ui-review-capability-comments__comment__content"):
                    comments_prod.append(comm.text)
                    # comments_prod.append(comm.find('p', class_="ui-review-capability-comments__comment__content").text)
            comments.append(comments_prod)
            
        df['Score'] = scores
        df['Ratings'] = ratings   
        df['Comments'] = comments

        print('Total products retrieved: {}'.format(df.shape[0]))
        display(df.head())
    
    elif pages_flag.__len__() == 0:
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

        # Add score, ratings and comments to the DataFrame
        scores = []
        ratings = []
        comments = []

        for i in range(df.__len__()):
            link_prod = df.loc[i, 'Link']
            request_ = requests.get(link_prod)
            content_ = request_.text
            soup_ = bs4.BeautifulSoup(content_, 'html.parser') # HTML document
            score_rating_tag_filter = soup_.find('div', {"class":"ui-review-capability"})#.find(class_="ui-review-capability__rating__average ui-review-capability__rating__average--desktop").text
            
            if score_rating_tag_filter == None:
                scores.append(0.0)
                ratings.append(0)
            else:
                scores.append(float(soup_.find('div', {"class":"ui-review-capability"}).find(class_="ui-review-capability__rating__average ui-review-capability__rating__average--desktop").text))
                ratings.append(int(re.match(r'[0-9]+',soup_.find('div', {"class":"ui-review-capability"}).find(class_="ui-review-capability__rating__label").text)[0]))

            comments_tag_filter = soup_.find_all('article', {"class":"ui-review-capability-comments__comment"})

            comments_prod = []
            if (comments_tag_filter == None) | (comments_tag_filter.__len__() == 0):
                comments_prod.append([])
            else:
                for comm in comments_tag_filter:
                    comments_prod.append(comm.find('p', class_="ui-review-capability-comments__comment__content").text)
            comments.append(comments_prod)
        
        df['Score'] = scores
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
def load_html_search_():
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
        if page == 1:
            url_page = 'https://listado.mercadolibre.com.mx/{}_NoIndex_True'.format(search.replace(' ','-'))
            request_page = requests.get(url_page)
            content_page = request_page.text
            soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
            tag_filter_page = soup_page.find_all("div", {"class":"ui-search-result__content-wrapper shops__result-content-wrapper"})

            for tag in tag_filter_page:
                brands.append(tag.find(class_="ui-search-item__brand-discoverability ui-search-item__group__element shops__items-group-details").text)
                products.append(tag.find("h2").text)
                prices.append(tag.find(class_="price-tag-fraction").text)
                links.append(tag.find("a")["href"])

        else:
            url_page = 'https://listado.mercadolibre.com.mx/{}_Desde_{}_NoIndex_True'.format(search.replace(' ','-'),(page*50)+1)
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
    data['Product'] = products
    data['Price'] = prices
    data["Link"] = links

    df = pd.DataFrame(data = data)
    df = df.drop_duplicates(ignore_index=True)
    df['Brand'] = df['Brand'].apply(lambda x: "-" if x == '' else x)
    df['Price'] = df['Price'].apply(lambda x: x.replace(",",""))
    df['Price'] = df['Price'].astype(int)

    # Add score, ratings and comments to the DataFrame
    scores = []
    ratings = []
    comments = []

    for i in range(df.__len__()):
        link_prod = df.loc[i, 'Link']
        request_ = requests.get(link_prod)
        content_ = request_.text
        soup_ = bs4.BeautifulSoup(content_, 'html.parser') # HTML document
        score_rating_tag_filter = soup_.find('div', {"class":"ui-review-capability"})#.find(class_="ui-review-capability__rating__average ui-review-capability__rating__average--desktop").text
        
        if (score_rating_tag_filter == None) | (score_rating_tag_filter.__len__() == 0):
            scores.append(0.0)
            ratings.append(0)
        else:
            scores.append(float(soup_.find('div', {"class":"ui-review-capability"}).find(class_="ui-review-capability__rating__average ui-review-capability__rating__average--desktop").text))
            ratings.append(int(re.match(r'[0-9]+',soup_.find('div', {"class":"ui-review-capability"}).find(class_="ui-review-capability__rating__label").text)[0]))

        comments_tag_filter = soup_.find_all('article', {"class":"ui-review-capability-comments__comment"})

        comments_prod = []
        if (comments_tag_filter == None) | (comments_tag_filter.__len__() == 0):
            comments_prod.append([])
        else:
            for comm in comments_tag_filter:
                comments_prod.append(comm.find('p', class_="ui-review-capability-comments__comment__content").text)
        comments.append(comments_prod)
    
    df['Score'] = scores
    df['Ratings'] = ratings   
    df['Comments'] = comments

    print('Total products retrieved: {}'.format(df.shape[0]))
    display(df.head())

    return df

def load_html_search_():
    search = input('Insert your search:')
    url = 'https://listado.mercadolibre.com.mx/{}#D[A:{}]'.format(search.replace(' ','-'), search)
    request = requests.get(url)
    print(f'Response status code: {request.status_code}')
    content = request.text
    soup = bs4.BeautifulSoup(content, 'html.parser') # HTML document
    pages_flag = soup.find_all("div", {"class":"ui-search-pagination shops__pagination-content"})
    print(pages_flag.__len__())

    if pages_flag.__len__() != 0:
    
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
            if page == 1:
                url_page = 'https://listado.mercadolibre.com.mx/{}_NoIndex_True'.format(search.replace(' ','-'))
                request_page = requests.get(url_page)
                content_page = request_page.text
                soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
                tag_filter_page = soup_page.find_all("div", {"class":"ui-search-result__content-wrapper shops__result-content-wrapper"})

                for tag in tag_filter_page:
                    brands.append(tag.find(class_="ui-search-item__brand-discoverability ui-search-item__group__element shops__items-group-details").text)
                    products.append(tag.find("h2").text)
                    prices.append(tag.find(class_="price-tag-fraction").text)
                    links.append(tag.find("a")["href"])

            else:
                url_page = 'https://listado.mercadolibre.com.mx/{}_Desde_{}_NoIndex_True'.format(search.replace(' ','-'),(page*50)+1)
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
        data['Product'] = products
        data['Price'] = prices
        data["Link"] = links

        df = pd.DataFrame(data = data)
        df = df.drop_duplicates(ignore_index=True)
        df['Brand'] = df['Brand'].apply(lambda x: "-" if x == '' else x)
        df['Price'] = df['Price'].apply(lambda x: x.replace(",",""))
        df['Price'] = df['Price'].astype(int)

        #df = df.copy().head(10)

        # Add score, ratings and comments to the DataFrame
        scores = []
        ratings = []
        comments = []

        for i in range(df.__len__()):
            link_prod = df.loc[i, 'Link']
            request_ = requests.get(link_prod)
            content_ = request_.text
            soup_ = bs4.BeautifulSoup(content_, 'html.parser') # HTML document
            score_rating_tag_filter = soup_.find('div', {"class":"ui-review-capability"})#.find(class_="ui-review-capability__rating__average ui-review-capability__rating__average--desktop").text
            
            if score_rating_tag_filter == None:
                scores.append(0.0)
                ratings.append(0)
            else:
                scores.append(float(soup_.find('div', {"class":"ui-review-capability"}).find(class_="ui-review-capability__rating__average ui-review-capability__rating__average--desktop").text))
                ratings.append(int(re.match(r'\d+',soup_.find('div', {"class":"ui-review-capability"}).find(class_="ui-review-capability__rating__label").text)[0]))  #r'[0-9]+'

            comments_tag_filter = soup_.find_all('article', {"class":"ui-review-capability-comments__comment"})

            comments_prod = []
            if (comments_tag_filter == None) | (comments_tag_filter.__len__() == 0):
                comments_prod.append([])
            else:
                for comm in comments_tag_filter:
                    comments_prod.append(comm.find('p', class_="ui-review-capability-comments__comment__content").text)
            comments.append(comments_prod)
        
        df['Score'] = scores
        df['Ratings'] = ratings   
        df['Comments'] = comments

        print('Total products retrieved: {}'.format(df.shape[0]))
        display(df.head())
    
    elif pages_flag.__len__() == 0:
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

        # Add score, ratings and comments to the DataFrame
        scores = []
        ratings = []
        comments = []

        for i in range(df.__len__()):
            link_prod = df.loc[i, 'Link']
            request_ = requests.get(link_prod)
            content_ = request_.text
            soup_ = bs4.BeautifulSoup(content_, 'html.parser') # HTML document
            score_rating_tag_filter = soup_.find('div', {"class":"ui-review-capability"})#.find(class_="ui-review-capability__rating__average ui-review-capability__rating__average--desktop").text
            
            if score_rating_tag_filter == None:
                scores.append(0.0)
                ratings.append(0)
            else:
                scores.append(float(soup_.find('div', {"class":"ui-review-capability"}).find(class_="ui-review-capability__rating__average ui-review-capability__rating__average--desktop").text))
                ratings.append(int(re.match(r'[0-9]+',soup_.find('div', {"class":"ui-review-capability"}).find(class_="ui-review-capability__rating__label").text)[0]))

            comments_tag_filter = soup_.find_all('article', {"class":"ui-review-capability-comments__comment"})

            comments_prod = []
            if (comments_tag_filter == None) | (comments_tag_filter.__len__() == 0):
                comments_prod.append([])
            else:
                for comm in comments_tag_filter:
                    comments_prod.append(comm.find('p', class_="ui-review-capability-comments__comment__content").text)
            comments.append(comments_prod)
        
        df['Score'] = scores
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
def load_html_search_():
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
        if page == 1:
            url_page = 'https://listado.mercadolibre.com.mx/{}_NoIndex_True'.format(search.replace(' ','-'))
            request_page = requests.get(url_page)
            content_page = request_page.text
            soup_page = bs4.BeautifulSoup(content_page, 'html.parser')
            tag_filter_page = soup_page.find_all("div", {"class":"ui-search-result__content-wrapper shops__result-content-wrapper"})

            for tag in tag_filter_page:
                brands.append(tag.find(class_="ui-search-item__brand-discoverability ui-search-item__group__element shops__items-group-details").text)
                products.append(tag.find("h2").text)
                prices.append(tag.find(class_="price-tag-fraction").text)
                links.append(tag.find("a")["href"])

        else:
            url_page = 'https://listado.mercadolibre.com.mx/{}_Desde_{}_NoIndex_True'.format(search.replace(' ','-'),(page*50)+1)
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
    data['Product'] = products
    data['Price'] = prices
    data["Link"] = links

    df = pd.DataFrame(data = data)
    df = df.drop_duplicates(ignore_index=True)
    df['Brand'] = df['Brand'].apply(lambda x: "-" if x == '' else x)
    df['Price'] = df['Price'].apply(lambda x: x.replace(",",""))
    df['Price'] = df['Price'].astype(int)

    # Add score, ratings and comments to the DataFrame
    scores = []
    ratings = []
    comments = []

    for i in range(df.__len__()):
        link_prod = df.loc[i, 'Link']
        request_ = requests.get(link_prod)
        content_ = request_.text
        soup_ = bs4.BeautifulSoup(content_, 'html.parser') # HTML document
        score_rating_tag_filter = soup_.find('div', {"class":"ui-review-capability"})#.find(class_="ui-review-capability__rating__average ui-review-capability__rating__average--desktop").text
        
        if (score_rating_tag_filter == None) | (score_rating_tag_filter.__len__() == 0):
            scores.append(0.0)
            ratings.append(0)
        else:
            scores.append(float(soup_.find('div', {"class":"ui-review-capability"}).find(class_="ui-review-capability__rating__average ui-review-capability__rating__average--desktop").text))
            ratings.append(int(re.match(r'[0-9]+',soup_.find('div', {"class":"ui-review-capability"}).find(class_="ui-review-capability__rating__label").text)[0]))

        comments_tag_filter = soup_.find_all('article', {"class":"ui-review-capability-comments__comment"})

        comments_prod = []
        if (comments_tag_filter == None) | (comments_tag_filter.__len__() == 0):
            comments_prod.append([])
        else:
            for comm in comments_tag_filter:
                comments_prod.append(comm.find('p', class_="ui-review-capability-comments__comment__content").text)
        comments.append(comments_prod)
    
    df['Score'] = scores
    df['Ratings'] = ratings   
    df['Comments'] = comments

    print('Total products retrieved: {}'.format(df.shape[0]))
    display(df.head())

    return df