from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import pandas as pd

def run():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    def crawl_levi_denim():  
        site= "https://www.calvinklein.co.kr/ko/men/apparel/denim-jeans/"
        
        try:
            req = Request(site, headers=headers)
            page = urlopen(req)
            soup = BeautifulSoup(page, 'html.parser')
        except Exception as e:
            print(f"Failed to fetch KC's data: {e}")
            return []

        products = []
        for item in soup.find_all("div", class_="product-tile"):
            try:
                product_name = item.find("div", class_="product-name-link")
                product_name = product_name.get_text(strip=True) if product_name else "Unknown"

                price_container = item.find("span", class_="sales")  # First, find the sales div
                price = price_container.find("span", class_="value") if price_container else None  # Then, find the nested value span
                price = price.get_text(strip=True) if price else "Not Available"

                promo = item.find("span", class_="percent-value")
                promo_info = promo.get_text(strip=True) if promo else "No Promotion"

                products.append({
                    "product": product_name,
                    "price": price,
                    "promotion": promo_info,
                    "source": "Cain Klein"

                })
            except Exception as e:
                print("Parsing error:", e)

        return products

    levi_data = crawl_levi_denim()

    levi_df = pd.DataFrame(levi_data)
    levi_df.to_csv("ck_products.csv", index=False)

    print("Extracted Levi's data:", levi_df.head())

if __name__ == "__main__":
    run()