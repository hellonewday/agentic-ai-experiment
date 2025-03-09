from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd

def run():
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    def crawl_lee_denim():  
        base_url = "https://leekorea.co.kr/category/%EB%8D%B0%EB%8B%98/760/?page={}"
        products = []

        def process_item(item, page):
            try:
                name_tag = item.find("div", class_="name")
                product_name = name_tag.get_text(strip=True) if name_tag else "Unknown"

                price_container = item.find("span", class_="sale")
                price = price_container.get_text().split(" ")[0]

                promo_tag = price_container.find("span") if price_container else None
                promotion = promo_tag.get_text(strip=True) if promo_tag else "No Promotion"

                products.append({
                    "product": product_name,
                    "price": price,
                    "promotion": promotion,
                    "source": "Lee Korea",
                })
            except Exception as e:
                print(f"Parsing error on page {page}: {e}")

        for page in range(1, 4):  # Loop over 3 pages
            print(f"Scraping page {page}...")

            try:
                req = Request(base_url.format(page), headers=HEADERS)
                page_data = urlopen(req)
                soup = BeautifulSoup(page_data, 'html.parser')

            except Exception as e:
                print(f"❌ Failed to fetch Lee Korea's page {page}: {e}")
                continue

            for item in soup.find_all("li", class_="product-item"):
                if "prd-first-banner" in item.get("class", []):
                    continue

                process_item(item, page)

        return products

    lee_data = crawl_lee_denim()

    lee_df = pd.DataFrame(lee_data)
    lee_df.to_csv("lee_products.csv", index=False)

    print("✅ Finished crawling Lee Korea data!")

if __name__ == "__main__":
    run()