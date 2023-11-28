import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import webbrowser
import requests
import bs4
from IPython.display import display
import spacy
from unidecode import unidecode
from sklearn.feature_extraction.text import CountVectorizer
from PIL import Image
from wordcloud import WordCloud

# spacy.cli.download("es_core_news_sm")
nlp = spacy.load("es_core_news_sm")


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
    print(f'Keywords: {search.replace("+"," ")}')
    url = f'https://www.amazon.com.mx/s?k={search}&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss'
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", 
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
    request = requests.get(url, headers=headers)
    content = request.text
    soup = bs4.BeautifulSoup(content, 'html.parser') # HTML document

    products = []
    prices = []
    stars = []
    links = [] 

    page_check = soup.find_all("div", class_="a-section a-text-center s-pagination-container")

    if page_check.__len__() != 0:
        print(f'Response status code: {request.status_code}')

        if soup.find("span", class_="s-pagination-item s-pagination-disabled") is not None:
            total_pages = int(soup.find("span", class_="s-pagination-item s-pagination-disabled").text)
            print(f'***************{soup.title.text}***************')
            print('Total pages: {}'.format(total_pages))
        else:
            total_pages = int(soup.find_all("a", class_="s-pagination-item s-pagination-button")[-1].text)
            print(f'***************{soup.title.text}***************')
            print('Total pages: {}'.format(total_pages))

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
                    products.append(tag.find("h2", class_="a-size-mini a-spacing-none a-color-base s-line-clamp-4").text)
                except:
                    products.append('-')

                try:
                    prices.append(int(tag.find("span", class_='a-price-whole').text.strip(".").replace(",","")))
                except:
                    prices.append(0)

                try:
                    stars.append(float(re.match(r'\d.\d',tag.find('span',class_="a-icon-alt").text)[0]))
                except:
                    stars.append(0.0)

                try:
                    links.append('https://www.amazon.com.mx/'+tag.find("a", class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")["href"])
                except:
                    links.append("-")

    elif soup.find("a", class_="s-pagination-item s-pagination-button") is None:
        print(f'Response status code: {request.status_code}')
        print(f'***************{soup.title.text}***************')
        print('Total pages: 1')
        
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

        for tag in tag_filter_page:
            try:
                products.append(tag.find("h2", class_="a-size-mini a-spacing-none a-color-base s-line-clamp-4").text)
            except:
                products.append('-')

            try:
                prices.append(int(tag.find("span", class_='a-price-whole').text.strip(".").replace(",","")))
            except:
                prices.append(0)

            try:
                stars.append(float(re.match(r'\d.\d',tag.find('span',class_="a-icon-alt").text)[0]))
            except:
                stars.append(0.0)

            try:
                links.append('https://www.amazon.com.mx/'+tag.find("a", class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")["href"])
            except:
                links.append("-")

    elif soup.find("a", class_="s-pagination-item s-pagination-button") is not None:
        print(f'Response status code: {request.status_code}')
        total_pages = int(soup.find_all("a", class_="s-pagination-item s-pagination-button")[-1].text)
        print(f'***************{soup.title.text}***************')
        print('Total pages: {}'.format(total_pages))

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
                    products.append(tag.find("h2", class_="a-size-mini a-spacing-none a-color-base s-line-clamp-4").text)
                except:
                    products.append('-')

                try:
                    prices.append(int(tag.find("span", class_='a-price-whole').text.strip(".").replace(",","")))
                except:
                    prices.append(0)

                try:
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

    print('\nProduct, price, stars and link - Done')
    print(df.shape)
    display(df.head(3))

    #Test
    # df = df.copy().head(10)
    # print('Copy made!!!!!!!!!!!!!')
    # print(df.shape)

    # Add ratings and comments to the DataFrame
    ratings = []
    ratings_mex = []
    num_comments = []
    comments_all = []
    comments_mex = []

    for i in range(df.__len__()):
        link_prod = df.loc[i, 'Link']
        request_ = requests.get(link_prod, headers=headers)
        content_ = request_.text
        soup_ = bs4.BeautifulSoup(content_, 'html.parser') # HTML document
        rating_comm_tag_filter = soup_.find(id="reviewsMedley")

        # print(f'Before: {type(rating_comm_tag_filter)}')

        attemps = 0
        while rating_comm_tag_filter is None and attemps < 101:
            link_prod = df.loc[i, 'Link']
            request_ = requests.get(link_prod, headers=headers)
            content_ = request_.text
            soup_ = bs4.BeautifulSoup(content_, 'html.parser') # HTML document
            rating_comm_tag_filter = soup_.find(id="reviewsMedley")
            attemps += 1

        # print(f'After: {type(rating_comm_tag_filter)}')
        # print(f'Attemps: {attemps}')

        comments_prod_all = []
        comments_prod_mx = []

        # Global Ratings
        if (rating_comm_tag_filter is None) or (rating_comm_tag_filter.find("span", class_="a-size-base a-color-secondary") is None):
            ratings.append(0)
        else:    
            ratings.append(int(re.search(r'\d+', rating_comm_tag_filter.find("span", class_="a-size-base a-color-secondary").text.strip().replace(",",""))[0]))

        # Global comments
        if (rating_comm_tag_filter is None) or (rating_comm_tag_filter.find_all("div", class_="a-expander-content reviewText review-text-content a-expander-partial-collapse-content").__len__() == 0):
            comments_prod_all.append('-')
        else:
            for comm in rating_comm_tag_filter.find_all("div", class_="a-expander-content reviewText review-text-content a-expander-partial-collapse-content"):
                comments_prod_all.append(comm.text.strip("\n") + '||')
        comments_all.append(comments_prod_all)

        # Number of global comments
        if (rating_comm_tag_filter is None) or (rating_comm_tag_filter.find_all("div", class_="a-expander-content reviewText review-text-content a-expander-partial-collapse-content").__len__() == 0): 
            num_comments.append(0)
        else:
            num_comments.append(rating_comm_tag_filter.find_all("div", class_="a-expander-content reviewText review-text-content a-expander-partial-collapse-content").__len__())

        # Mexico comments
        if (rating_comm_tag_filter is None) or (rating_comm_tag_filter.find("div", class_="cm-cr-dp-review-list") is None): 
            comments_prod_mx.append('-')
        else:
            for comm_mx in rating_comm_tag_filter.find("div", id="cm-cr-dp-review-list").find_all("div", class_="a-expander-content reviewText review-text-content a-expander-partial-collapse-content"):
                comments_prod_mx.append(comm_mx.text.strip("\n") + '||')
        comments_mex.append(comments_prod_mx) 

        # if (rating_comm_tag_filter is None) or (rating_comm_tag_filter.find_all("div", class_="cm-cr-dp-review-list").__len__() == 0): 
        #     print(rating_comm_tag_filter.find_all("div", class_="cm-cr-dp-review-list"))
        #     comments_prod_mx.append('-')
        # else:
        #     for comm in rating_comm_tag_filter.find("div", class_="cm-cr-dp-review-list").find_all("div", class_="a-expander-content reviewText review-text-content a-expander-partial-collapse-content"):
        #         for txt in comm:
        #             print(txt)
        #             comments_prod_mx.append(txt.text.strip("\n") + '||')
        # comments_mex.append(comments_prod_mx)

        # if (rating_comm_tag_filter is None) or (rating_comm_tag_filter.find_all("div", class_="cm-cr-global-review-list").__len__() == 0): 
        #     comments_prod_all.append('-')
        # else:
        #     for comm in rating_comm_tag_filter.find_all("div", class_="cm-cr-global-review-list"):  ###### .find("div",id='cm-cr-dp-review-list')
        #         comments_prod_all.append(comm.find("div", class_="a-expander-content reviewText review-text-content a-expander-partial-collapse-content").text.strip("\n") + '||')
        # # comments_prod.append(comm.text.strip("\n"))
        # comments_all.append(comments_prod_all)

    df['Global Ratings'] = ratings
    # df['Ratings MX'] = ratings_mex
    df['Num. Global Comments'] = num_comments
    df['Global Comments'] = comments_all
    df['Comments MX'] = comments_mex

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

def preprocess(text, min_len=1, max_len=23):
    pat = re.compile(r"[^a-z ]")
    spaces = re.compile(r"\s{2,}")
    # spacy Doc creation
    doc = nlp(text)
    # Remove stopwords
    filtered_tokens = filter(
            lambda token: not token.is_stop,
            doc
            )
    # Filter words by length and remove stop words
    filtered_tokens2 = filter(
            lambda token: len(token) >= min_len and len(token) <= max_len and not token.is_stop,
            filtered_tokens
        )
    # Lemmatization
    lemmas = map(
            lambda token: token.lemma_,
            filtered_tokens2
            )
    lemma_text = " ".join(lemmas)
    # Normalize text
    norm_text = unidecode(lemma_text)
    # Remove accents
    lower_text = norm_text.lower()
    # Remove special characters
    clean_text = re.sub(pat, "", lower_text)
    # Remomove duplicate spaces (if exist)
    spaces_text = re.sub(spaces, " ", clean_text)
    return spaces_text.strip()

def word_cloud(prep_corpus):
    vect = (CountVectorizer(max_features=1000, max_df=0.7).fit(prep_corpus))
    X = vect.transform(prep_corpus)
    vocab = vect.get_feature_names_out()
    counts = np.array(X.sum(axis=0)).flatten()
    counts_dict = {word: count for word, count in zip(vocab, counts)}
    mask = np.array(Image.open("C:/Users/nicarang/OneDrive - Publicis Groupe/Documentos/Digitas/P&G/Benchmarking/cloud.png"))

    wc = WordCloud(background_color='white',
        width=3000,
        height=2000,
        collocations=False,
        mask=mask,
        colormap = 'Dark2',
        max_words=40
                    ).generate_from_frequencies(counts_dict)

    plt.figure(figsize=[7,7])
    plt.imshow(wc,interpolation="bilinear")
    plt.axis("off") 
    plt.show()

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