
import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List, Dict

OUEST_FRANCE_IMMO_URL = "https://www.ouestfrance-immo.com/acheter/appartement/rennes-35-35000/?page="


def extract_data_from_ads(ads: List[Tag]) -> pd.DataFrame:
    type = []
    place = []
    price = []
    for i, ad in enumerate(ads):
        ad_premium = ad.find("div", {"class": "premium multi-photos"})
        if ad_premium:
            print(f"ad number {i} is a premium ad, skiping")
        else:
            try:
                type_i = ad.find("span", {"class": "annTitre"}).text.strip()
                place_i = ad.find("span", {"class": "annVille"}).text.strip()
                price_i = ad.find("span", {"class": "annPrix"}).text.strip()
                place.append(place_i)
                print(f"annonce {i} : {type.strip()} - {place.strip()} - {price.strip()}")
            except AttributeError as error:
                type_i = ad.find('h3').find("span", {"class": "annTitre"}).text.strip()
                price_i = ad.find('h3').find("span", {"class": "annPrix"}).text.strip()

            type.append(type_i)
            price.append(price_i)
            place.append("NA")

    return pd.DataFrame(data=list(zip(type, place, price)), columns=["type_apt", "place", "price"])


def request_page(n: int) -> BeautifulSoup:
    url = OUEST_FRANCE_IMMO_URL + str(n)
    page = requests.open(url)
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
