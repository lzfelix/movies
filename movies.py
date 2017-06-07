from urllib.request import urlopen
from bs4 import BeautifulSoup

def get_movies_table(soup):
    """Identifies and returns the table containing movie titles and exibition times."""
    body = soup.body
    movies_table = body.table.next_sibling.next_sibling.table
    movies_rows = movies_table.find_all('tr')

    # the last table rows contain price and disclaimer information
    n = len(movies_rows) - 7

    return [(title, description) for title, description in zip(movies_rows[2:n:2], movies_rows[3:n:2])]


def get_title(raw_title):
    """Given an HTML table row, returns just the movie title."""
    pass


def get_description(raw_description):
    """Given an HTML table row, returns the exhibiting cinemas and times."""
    pass


def extract_details_from_raw(raw_details):
    return {get_title(raw_title): get_description(raw_description) for (raw_title, raw_description) in raw_details}


if __name__ == '__main__':
    # body = urlopen('http://www.jcnet.com.br/cinema/').read()
    with open('tests/page.html', encoding='latin1') as file:
        body = file.read()
        file.close()        

    soup = BeautifulSoup(body, "lxml")
    movies_table = get_movies_table(soup)
    details = extract_details_from_raw(movies_table)

    print(details)
    