import urllib.request
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://www.mobafire.com"
BASE_URL_GAME_LOL = BASE_URL + "/league-of-legends/"
BASE_URL_GUIDE_LIST_POSTFIX = "browse"


def get_specific_guide_url(url):
    return BASE_URL + url


def get_page_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    }

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')
    return data


def get_soup_from_browse_url(browse_url=BASE_URL_GAME_LOL + BASE_URL_GUIDE_LIST_POSTFIX):
    html_content = get_page_html(browse_url)
    return browse_url, BeautifulSoup(html_content, 'html.parser')


def get_next_page_url(soup):
    next_page_div = soup.find("div", class_="browse-pager__next")
    if next_page_div:
        next_page_link = next_page_div.find('a', href=True)
        return BASE_URL + next_page_link['href']
    return None


def get_guides(soup):
    links = [a['href'] for a in soup.find_all('a', class_='mf-listings__item')]
    return [get_specific_guide_url(x) for x in links]


def parse_guide(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract general info
    header_div = soup.find("div", class_="view-guide__header__top")
    champion_name = header_div.find(
        'span', class_='mobile-sr').text.split("Build Guide by")[0].strip()
    author_tag = header_div.find('a', class_='user-level')
    author_name = author_tag.text
    author_link = BASE_URL + author_tag['href']
    date = soup.find('span', class_='localized-datetime').text

    # Helper function to extract threat/synergy data
    def extract_data(div, category):
        def safe_text(tag):
            return tag.text if tag else None

        return [{
            'champion': champion_name,
            'author': author_name,
            'author_link': author_link,
            'date': date,
            'category': category,
            'target_hero': safe_text(row.find('h4')),
            'level': safe_text(row.find('label')),
            'comment': safe_text(row.find('p'))
        } for row in div.find_all("div", class_="row")]

    # Extract threats and synergies
    threat_div = soup.find("div", class_="view-guide__tS__bot__left collapsed")
    synergy_div = soup.find(
        "div", class_="view-guide__tS__bot__right collapsed")

    threats = extract_data(threat_div, "Threat") if threat_div else []
    synergies = extract_data(synergy_div, "Synergy") if synergy_div else []

    return threats + synergies


def get_champion_pages(soup):
    links = [a['href']
             for a in soup.find_all('a', class_='champ-list__item visible')]
    return [get_specific_guide_url(x) for x in links]


def get_top_guides(soup):
    rated_links = []

    # Fetch the relevant elements
    guides_box = soup.find_all('a', class_='mf-listings__item')
    for i in guides_box:
        rating_tag = i.find(
            'div', class_='mf-listings__item__rating__circle__inner').find('span')
        if rating_tag is not None:
            rating = float(rating_tag.text)
            rated_links.append((rating, i['href']))

    # Sort the links by rating in descending order and fetch the top 3
    top_links = [link for _, link in sorted(
        rated_links, key=lambda x: x[0], reverse=True)[:3]]
    return top_links


def get_champion_name(soup):
    return {'champion_name': soup.find('div', class_='champ__splash__title').find('h2').contents[0].strip(),
            'champion_alias': soup.find('div', class_='champ__splash__title').find('h2').find('span').text.strip()}


def get_champion_abilities(soup):
    passive_abilities = [{'ability_name': x.find('div', class_='champ__abilities__item__name').contents[0].strip(
    ), 'ability_type': 'passive',  'ability_range': x.find('div', class_='champ__abilities__item__range').text.strip(
    ), 'ability_description': x.find('div', class_='champ__abilities__item__desc').text.strip(
    )} for x in soup.find_all('a', class_='champ__abilities__item champ__abilities__item--passive')]

    abilities = [{'ability_name': x.find('div', class_='champ__abilities__item__name').contents[0].strip(
    ), 'ability_type': x.find('div', class_='champ__abilities__item__letter').text.strip(
    ), 'ability_range': x.find('div', class_='champ__abilities__item__range').text.strip(
    ), 'ability_description': x.find('div', class_='champ__abilities__item__desc').text.strip(
    )} for x in soup.find_all('a', class_='champ__abilities__item') if x.find('div', class_='champ__abilities__item__letter') is not None]
    return passive_abilities, abilities
