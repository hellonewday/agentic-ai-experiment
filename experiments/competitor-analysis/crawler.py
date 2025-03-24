import logging
from crewai.tools import BaseTool
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import pandas as pd
from typing import List, Dict

class CompetitorCrawler(BaseTool):
    """Tool to crawl and clean product data from Levi's Korea, Lee Korea, and Calvin Klein Korea."""
    name: str = "Crawl Competitor Data"
    description: str = "Crawls price and promotion data from Levi's Korea, Lee Korea, and Calvin Klein Korea, cleaning it immediately."

    def _clean_price(self, price: str) -> int | None:
        """Clean price by removing non-digits and converting to integer."""
        if not isinstance(price, str):
            return None
        price = re.sub(r"[^\d]", "", price)
        return int(price) if price.isdigit() else None

    def _clean_promotion(self, promo: str) -> str:
        """Clean promotion by extracting digits and formatting as percentage."""
        if not isinstance(promo, str):
            return "No Promotion"
        promo = re.sub(r"[^\d]", "", promo)
        return f"{promo}%" if promo else "No Promotion"

    def _run(self) -> List[Dict]:
        """Crawl data from all three websites, clean it immediately, and return standardized product details."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        all_products = []

        # Levi's Korea Crawler
        levi_url = "https://www.levi.co.kr/%EB%82%A8%EC%84%B1/%EC%9D%98%EB%A5%98/%EC%A7%84"
        try:
            req = Request(levi_url, headers=headers)
            page = urlopen(req)
            soup = BeautifulSoup(page, "html.parser")
            logging.info("Successfully fetched Levi's Korea data")
            for item in soup.find_all("div", class_="product-tile"):
                try:
                    product_name = item.find("div", class_="name1") or "Unknown"
                    product_name = product_name.get_text(strip=True) if product_name != "Unknown" else "Unknown"
                    price = item.find("span", class_="product-sales-price")
                    price = price.get_text(strip=True) if price else "Not Available"
                    promo = item.find("div", class_="discount-amount")
                    promo_info = promo.get_text(strip=True) if promo else "No Promotion"
                    all_products.append({
                        "product": product_name,
                        "price": self._clean_price(price),
                        "promotion": self._clean_promotion(promo_info),
                        "source": "Levis"
                    })
                except Exception as e:
                    logging.warning(f"Levi's parsing error: {e}")
        except Exception as e:
            logging.error(f"Failed to fetch Levi's data: {e}")

        # Lee Korea Crawler
        lee_base_url = "https://leekorea.co.kr/category/%EB%8D%B0%EB%8B%98/760/?page={}"
        for page in range(1, 4):
            try:
                req = Request(lee_base_url.format(page), headers=headers)
                page_data = urlopen(req)
                soup = BeautifulSoup(page_data, "html.parser")
                logging.info(f"Successfully fetched Lee Korea page {page}")
                for item in soup.find_all("li", class_="product-item"):
                    if "prd-first-banner" in item.get("class", []):
                        continue
                    try:
                        name_tag = item.find("div", class_="name")
                        product_name = name_tag.get_text(strip=True) if name_tag else "Unknown"
                        price_container = item.find("span", class_="sale")
                        price = price_container.get_text().split(" ")[0] if price_container else "Not Available"
                        promo_tag = price_container.find("span") if price_container else None
                        promotion = promo_tag.get_text(strip=True) if promo_tag else "No Promotion"
                        all_products.append({
                            "product": product_name,
                            "price": self._clean_price(price),
                            "promotion": self._clean_promotion(promotion),
                            "source": "Lee Korea"
                        })
                    except Exception as e:
                        logging.warning(f"Lee Korea parsing error on page {page}: {e}")
            except Exception as e:
                logging.error(f"Failed to fetch Lee Korea page {page}: {e}")

        # Calvin Klein Korea Crawler
        ck_url = "https://www.calvinklein.co.kr/ko/men/apparel/denim-jeans/"
        try:
            req = Request(ck_url, headers=headers)
            page = urlopen(req)
            soup = BeautifulSoup(page, "html.parser")
            logging.info("Successfully fetched Calvin Klein Korea data")
            for item in soup.find_all("div", class_="product-tile"):
                try:
                    product_name = item.find("div", class_="product-name-link") or "Unknown"
                    product_name = product_name.get_text(strip=True) if product_name != "Unknown" else "Unknown"
                    price_container = item.find("span", class_="sales")
                    price = price_container.find("span", class_="value") if price_container else None
                    price = price.get_text(strip=True) if price else "Not Available"
                    promo = item.find("span", class_="percent-value")
                    promo_info = promo.get_text(strip=True) if promo else "No Promotion"
                    all_products.append({
                        "product": product_name,
                        "price": self._clean_price(price),
                        "promotion": self._clean_promotion(promo_info),
                        "source": "Calvin Klein"
                    })
                except Exception as e:
                    logging.warning(f"Calvin Klein parsing error: {e}")
        except Exception as e:
            logging.error(f"Failed to fetch Calvin Klein data: {e}")

        if all_products:
            pd.DataFrame(all_products).to_csv("cleaned_products.csv", index=False)
            logging.info(f"Saved {len(all_products)} cleaned products to cleaned_products.csv")

        return all_products