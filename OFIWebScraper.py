
import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List, Dict, Tuple

OUEST_FRANCE_IMMO_URL = "https://www.ouestfrance-immo.com/acheter/appartement/rennes-35-35000/?page="


def extract_announce_criterias(ad: Tag) -> Tuple[str]:
    """
    Extract criterias from ad tag
    @param ad:  an ad bs4 tag
    @return: surface, nb bedroom, nb shower Tuple collection
    """
    nb_bedroom = 0
    nb_sdb = 0
    surface = "NA"

    try:
        criterias = ad.find("span", {"class": "annCriteres"}).find_all("div")
        if criterias:
            for criteria in criterias:
                value = criteria.text.strip()
                unit = criteria.find("span", {"class": "unit"}).text.strip()
                if "chb" == unit:
                    nb_bedroom = value.replace("chb", "").strip()
                elif "sdb" == unit:
                    nb_sdb = value.replace("sdb", "").strip()
                else:
                    surface = value.replace(value[value.find("m"):], "")
    except AttributeError:
        print("No criterias on this ad")

    return surface, nb_bedroom, nb_sdb


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
    type, place, price, surface, bedroom, sdb = [], [], [], [], [], [],

    for i, ad in enumerate(ads):
        ad_premium = ad.find("div", {"class": "premium multi-photos"})
        if ad_premium:
            print(f"ad number {i} is a premium ad, skiping")
        else:
            type_i = extract_announce_title(ad)
            place_i = extract_announce_place(ad)
            price_i = extract_announce_price(ad)
            surface_i, nb_bedroom_i, nb_sdb_i = extract_announce_criterias(ad)

            type.append(type_i)
            price.append(price_i)
            place.append(place_i)
            surface.append(surface_i)
            bedroom.append(nb_bedroom_i)
            sdb.append(nb_sdb_i)

    return pd.DataFrame(data=list(zip(type, place, bedroom, sdb, surface, price)),
                        columns=["type_apt", "place", "bedroom", "sdb", "surface", "price"])


def request_page(n: int) -> BeautifulSoup:
    url = OUEST_FRANCE_IMMO_URL + str(n)
    page = requests.get(url)
    return BeautifulSoup(page.content, features="lxml")


if __name__ == '__main__':
    page_i = 1
    soup = request_page(page_i)
    total_ads = int(soup.find("strong", {"class": "enteteNb"}).text.strip().replace(" ", ""))
    df_ads = pd.DataFrame(columns=["type_apt", "place", "bedroom", "sdb", "surface", "price"])

    while total_ads > 0:
        soup = request_page(page_i)
        ads = soup.findAll("a", {"class": "annLink"})
        df = extract_data_from_ads(ads)
        df_ads = pd.concat([df_ads, df], axis=0)

        page_i += 1
        total_ads -= len(ads)

    print(df_ads)
