import re
import string
import json

from urllib.request import urlopen
from bs4 import BeautifulSoup
from bs4.element import Tag

from pprint import pprint as pp


def get_movies_table(soup):
    """Identifies and returns the table containing movie titles and exibition
    times."""

    body = soup.body

    # This will lead to the 2nd level table that contains all movie data
    movies_table = body.table.next_sibling.next_sibling.table
    movies_rows = movies_table.find_all('tr')

    # the last table rows contain price and disclaimer information
    n = len(movies_rows) - 7

    return [(title, description) for title, description in
            zip(movies_rows[2:n:2], movies_rows[3:n:2])]


def get_title(raw_title):
    """Given an HTML table row, returns just the movie title."""

    # TODO: this can be improved to be language-dependant
    return string.capwords(raw_title.td.string)


def get_venues(raw_details):
    # raw_details is a paragraph

    strongs = raw_details.find_all('strong')
    venue = strongs[0].text                # Cine'n fun, Cinepolis or Multiplex

    exhibitions = list()
    for strong in strongs[1:]:
        mode = strong.text

        # Session times are sometimes interleaved with <br> taegs. Loop over
        # all of them
        accumulator = str()
        sessions = strong.next_sibling
        while sessions:
            if type(sessions) is Tag:
                sessions = sessions.next_sibling

            # str() words either for Tags and NavigableStrings
            accumulator += str(sessions)
            sessions = sessions.next_sibling

        # Adding space between rooms. Getting rid of annoying \n and <br/?>s.
        # This part can be probably improved.
        accumulator = re.sub('Sala', ' Sala', accumulator)
        accumulator = re.sub(r'(\n|<br/?>|\s{2,})', '', accumulator).strip()

        # Done with this batch. Put everything togheter.
        exhibitions.append({'type': mode, 'times': accumulator})

    return {venue: exhibitions}


def get_description(raw_description):
    """Given an HTML table row, returns the exhibiting cinemas and times."""

    text_rows = raw_description.find_all('td', class_='font14')
    if not text_rows:
        raise ValueError('Could not find row containing the movie synopsis. ' +
                         'has the page HTML changed?')

    # The first row contains all the movie information. Before the <p> tag,
    # which is translated as [\n] there is the movie synopsis.
    all_text = text_rows[0].text

    # 1. The movie synopsis can be extracted directly
    synopsis = all_text[:all_text.find('\n')].strip()

    # For exhibition times and locatinos, it's better to be guided by the
    # paragraphs
    paragraphs = text_rows[0].find_all('p')
    if not paragraphs:
        raise ValueError('Could not find movie exhibitino times. Has the ' +
                         'page layout changed?')

    # Movie metadata is stored on the 1st paragraph as sequence of <strong>
    metadata = paragraphs[0].find_all('strong')
    if not metadata or len(metadata) < 2:
        raise ValueError('Falied to determine movie metadata.')

    # 2. Got genre and duration!
    genre = metadata[0].next_sibling
    duration = metadata[1].next_sibling.strip()

    # 3. Movie sessions
    venues = [get_venues(raw_details) for raw_details in paragraphs[2:]]

    return {
        'genre': genre,
        'duration': duration,
        'synopsis': synopsis,
        'venues': venues
    }


def get_movie(raw_title, raw_description):
    title = get_title(raw_title)
    details = get_description(raw_description)

    return {
        'title': title,
        'details': details
    }


if __name__ == '__main__':
    # body = urlopen('http://www.jcnet.com.br/cinema/').read()
    with open('tests/page.html', encoding='latin1') as file:
        body = file.read()
        file.close()

    soup = BeautifulSoup(body, "lxml")
    movies_table = get_movies_table(soup)

    movies = [get_movie(raw_title, raw_description)
              for (raw_title, raw_description) in movies_table]

    # pp(movies)
    print(json.dumps(movies))
