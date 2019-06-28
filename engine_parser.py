import requests
from bs4 import BeautifulSoup
from datetime import datetime

import sys


class EngineParser:
    def __init__(self, engine='google'):
        # Headers for imitation user activity
        self.__HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

        # Set engine
        self.ENGINE = engine.lower()

    def __fetch_results(self, query, number, language_code):
        url = ''
        # preparation of request link
        if self.ENGINE == 'bing':
            url = 'https://www.bing.com/search?q={}&count={}'.format(query, number)
        elif self.ENGINE == 'google':
            url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(query, number, language_code)

        # get page with timeout = 5sec (for imitation user activity)
        response = requests.get(url, headers=self.__HEADERS, timeout=5)

        # error checking
        response.raise_for_status()

        # return HTML code of page
        return response.text

    def __parse_bing_html(self, html, query):
        soup = BeautifulSoup(html, 'lxml')

        found_results = []
        index = 1
        result_block = soup.find_all('li', attrs={'class': 'b_algo'})
        for result in result_block:

            link = result.find('a', href=True)
            title = result.find('h2')
            description = result.find('p')
            if link and title:
                link = link['href']
                title = title.get_text()
                if description:
                    description = description.get_text()
                if link != '#' and description is not None:
                    found_results.append({'index': index, 'query': query,
                                          'link': link, 'title': title,
                                          'description': description,
                                          'time': datetime.now()})
                    index += 1
        return found_results

    def __parse_google_html(self, html, query):
        soup = BeautifulSoup(html, 'lxml')

        found_results = []
        index = 1
        result_block = soup.find_all('div', attrs={'class': 'g'})
        for result in result_block:

            link = result.find('a', href=True)
            title = result.find('h3')
            description = result.find('span', attrs={'class': 'st'})
            if link and title:
                link = link['href']
                title = title.get_text()
                if description:
                    description = description.get_text()
                if link != '#' and description is not None:
                    found_results.append({'index': index, 'query': query,
                                          'link': link, 'title': title,
                                          'description': description,
                                          'time': datetime.now()})
                    index += 1
        return found_results

    def __scrape(self, query, number, language_code):
        try:
            html = self.__fetch_results(query, number, language_code)
            if self.ENGINE == 'bing':
                return self.__parse_bing_html(html=html, query=query)
            elif self.ENGINE == 'google':
                return self.__parse_google_html(html=html, query=query)
        except AssertionError:
            raise Exception("Incorrect arguments parsed to function")
        except requests.HTTPError:
            raise Exception("You appear to have been blocked by Google")
        except requests.RequestException:
            raise Exception("Appears to be an issue with your connection")

    def start_engine_scrapping(self, query, number, language_code, print_output=False, engine='google'):
        self.ENGINE = engine.lower()
        results = self.__scrape(query=query, number=number, language_code=language_code)

        if print_output:
            for i in results:
                print(i)

        return results


if '__main__' == __name__:
    """
    query                   <--->       your search query
    number                  <--->       how many links you want to see
    language_code           <--->       code of language of your query

    How to run this script? (example):
        python main.py "право постійного користування земельною ділянкою" 3 ru
    """
    engine_parser = EngineParser('Google')
    engine_parser.start_engine_scrapping(query=sys.argv[1], number=int(sys.argv[2]),
                                         language_code=sys.argv[3], print_output=True)