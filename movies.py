from urllib.request import urlopen
from bs4 import BeautifulSoup
import string

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

    # TODO: this can be improved to be language-dependant
    return string.capwords(raw_title.td.string)


def get_description(raw_description):
    """Given an HTML table row, returns the exhibiting cinemas and times."""

    text_rows = raw_description.find_all('td', class_='font14')
    if not text_rows:
        raise ValueError('Could not find row containing movie data. Has the page HTML changed?')

    # The first row contains all the movie information. Before the <p> tag, which is translated
    # as [\n] there is the movie synopsis.

    all_text = text_rows[0].text
    synopsis = all_text[:all_text.find('\n')].strip()

    data = dict()
    data['synopsis'] = synopsis

    return data


# def extract_details_from_raw(raw_details):
#     return {get_title(raw_title): get_description(raw_description) for (raw_title, raw_description) in raw_details}


if __name__ == '__main__':
    # body = urlopen('http://www.jcnet.com.br/cinema/').read()
    with open('tests/page.html', encoding='latin1') as file:
        body = file.read()
        file.close()

    soup = BeautifulSoup(body, "lxml")
    movies_table = get_movies_table(soup)
    
    frame = [(get_title(raw_title), get_description(raw_description)) for (raw_title, raw_description) in movies_table]

    print(frame)
    