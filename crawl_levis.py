from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import pandas as pd

def run():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    def crawl_levi_denim():  
        site= "https://www.levi.co.kr/%EB%82%A8%EC%84%B1/%EC%9D%98%EB%A5%98/%EC%A7%84"
        
        try:
            req = Request(site, headers=headers)
            page = urlopen(req)
            soup = BeautifulSoup(page, 'html.parser')
        except Exception as e:
            print(f"Failed to fetch Levi's data: {e}")
            return []

        products = []
        for item in soup.find_all("div", class_="product-tile"):
            try:
                product_name = item.find("div", class_="name1")
                product_name = product_name.get_text(strip=True) if product_name else "Unknown"

                price = item.find("span", class_="product-sales-price")
                price = price.get_text(strip=True) if price else "Not Available"
                price = re.sub(r"[^\d]", "", price)  # Clean price format (remove ₩)

                promo = item.find("div", class_="discount-amount")
                promo_info = promo.get_text(strip=True) if promo else "No Promotion"

                products.append({
                    "product": product_name,
                    "price": price,
                    "promotion": promo_info,
                    "source": "Levis"
                })
            except Exception as e:
                print("Parsing error:", e)

        return products

    levi_data = crawl_levi_denim()

    levi_df = pd.DataFrame(levi_data)
    levi_df.to_csv("levi_products.csv", index=False)

    print("✅ Finished crawling Levis Korea data!")

if __name__ == "__main__":
    run()