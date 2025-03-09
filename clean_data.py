import pandas as pd
import re

def run():
    def clean_price(price):
        if not isinstance(price, str):
            return None
        price = re.sub(r"[^\d]", "", price)
        return int(price) if price.isdigit() else None

    def clean_promotion(promo):
        if not isinstance(promo, str):
            return "No Promotion"
        promo = re.sub(r"[^\d]", "", promo)
        return f"{promo}%" if promo else "No Promotion"

    levi_df = pd.read_csv("levi_products.csv")
    ck_df = pd.read_csv("ck_products.csv")
    lee_df = pd.read_csv("lee_products.csv")

    for df in [levi_df, ck_df, lee_df]:
        df["price"] = df["price"].apply(clean_price)
        df["promotion"] = df["promotion"].apply(clean_promotion)

    merged_df = pd.concat([levi_df, ck_df, lee_df], ignore_index=True)
    merged_df.to_csv("cleaned_products.csv", index=False)

    print("✅ Cleaning completed!")

if __name__ == "__main__":
    run()