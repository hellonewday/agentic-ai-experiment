import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def run():
    df = pd.read_csv("cleaned_products.csv")
    df = df.fillna("No Data")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    df["text"] = df.apply(lambda row: f"{row['product']} - {row['price']} - {row['promotion']} - {row['source']}", axis=1)

    embeddings = model.encode(df["text"].tolist(), convert_to_numpy=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    faiss.write_index(index, "products_faiss.index")
    df.to_csv("metadata.csv", index=False)

    print("✅ Embeddings stored successfully in FAISS!")

if __name__ == "__main__":
    run()