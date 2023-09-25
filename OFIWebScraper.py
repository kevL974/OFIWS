
import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List, Dict

OUEST_FRANCE_IMMO_URL = "https://www.ouestfrance-immo.com/acheter/appartement/rennes-35-35000/?page="


def extract_announce_title(ad: Tag) -> str:
    """
    Extract title from ad tag
    @param ad:  an ad bs4 tag
    @return: title in string format
    """
    try:
        return ad.find("span", {"class": "annTitre"}.text.strip())
    except AttributeError:
        if ad.find('h3').find("span", {"class": "annTitre"}) is None:
            return "NA"
        else:
            return ad.find('h3').find("span", {"class": "annTitre"}).text.strip()


def extract_announce_place(ad: Tag) -> str:
    """
    Extract place from ad tag
    @param ad:  an ad bs4 tag
    @return: place in string format
    """
    try:
        return ad.find("span", {"class": "annVille"}).text.strip()
    except AttributeError:
        return "NA"


def extract_announce_price(ad: Tag) -> str:
    """
    Extract price from ad tag
    @param ad:  an ad bs4 tag
    @return: price in string format
    """
    try:
        return ad.find("span", {"class": "annPrix"}).text.strip()
    except AttributeError:
        if ad.find('h3').find("span", {"class": "annPrix"}) is None:
            return "NA"
        else:
            return ad.find('h3').find("span", {"class": "annPrix"}).text.strip()


def extract_data_from_ads(ads: List[Tag]) -> pd.DataFrame:
    type = []
    place = []
    price = []
    for i, ad in enumerate(ads):
        ad_premium = ad.find("div", {"class": "premium multi-photos"})
        if ad_premium:
            print(f"ad number {i} is a premium ad, skiping")
        else:
            type_i = extract_announce_title(ad)
            place_i = extract_announce_place(ad)
            price_i = extract_announce_price(ad)

            type.append(type_i)
            price.append(price_i)
            place.append(place_i)

    return pd.DataFrame(data=list(zip(type, place, price)), columns=["type_apt", "place", "price"])


def request_page(n: int) -> BeautifulSoup:
    url = OUEST_FRANCE_IMMO_URL + str(n)
    page = requests.get(url)
    return BeautifulSoup(page.content, features="lxml")


if __name__ == '__main__':
    page_i = 1
    soup = request_page(page_i)
    total_ads = int(soup.find("strong", {"class": "enteteNb"}).text.strip().replace(" ", ""))
    df_ads = pd.DataFrame(columns=["type_apt", "place", "price"])

    while total_ads > 0:
        soup = request_page(page_i)
        ads = soup.findAll("a", {"class": "annLink"})
        df = extract_data_from_ads(ads)
        df_ads = pd.concat([df_ads, df], axis=0)

        page_i += 1
        total_ads -= len(ads)

    print(df_ads)
