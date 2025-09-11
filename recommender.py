import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from implicit.als import AlternatingLeastSquares
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

orders = pd.read_csv("orders_merged.csv")
products = pd.read_csv("products_cleaned.csv")

order_details = pd.merge(orders, products, on="product_id", how="left")
product_popularity = (
    order_details.groupby("product_id").size()
    .reset_index(name="purchase_count")
    .sort_values("purchase_count", ascending=False)
)

user_index = orders["user_id"].unique()
item_index = orders["product_id"].unique()

user_index_map = {u: i for i, u in enumerate(user_index)}
item_index_map = {p: i for i, p in enumerate(item_index)}

row = orders["user_id"].map(user_index_map)
col = orders["product_id"].map(item_index_map)
data = np.ones(len(orders))
user_item_csr = csr_matrix((data, (row, col)), shape=(len(user_index), len(item_index)))

als_model = AlternatingLeastSquares(factors=20, regularization=0.1, iterations=20)
als_model.fit(user_item_csr)
item_index = np.array(item_index)

products["products_cleaned"] = (
    products["product_name"].astype(str) + " " +
    products["aisle"].astype(str) + " " +
    products["department"].astype(str)
)
product_metadata = products[["product_id", "products_cleaned"]].drop_duplicates().reset_index(drop=True)

tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(product_metadata["products_cleaned"])

id_to_index = pd.Series(product_metadata.index, index=product_metadata["product_id"])
index_to_id = pd.Series(product_metadata["product_id"].values, index=product_metadata.index)


def recommend_als_safe(raw_user_id, N=5):
    if raw_user_id not in user_index:
        return product_popularity.head(N)["product_id"].tolist()
    uidx = np.where(user_index == raw_user_id)[0][0]
    ids, _ = als_model.recommend(uidx, user_item_csr[uidx], N=N, filter_already_liked_items=True)
    return [int(item_index[i]) for i in ids]


def recommend_content(product_id, N=5):
    if product_id not in id_to_index:
        return []
    idx = id_to_index[product_id]
    sim_scores = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).ravel()
    top_indices = sim_scores.argsort()[::-1][1:N+1]
    return index_to_id[top_indices].tolist()
