import pandas as pd

products = pd.read_csv("data/products.csv")

def get_recommendations(cart_items):
    categories = products[products['product_id'].isin(cart_items)]['category'].unique()
    recs = products[products['category'].isin(categories) & ~products['product_id'].isin(cart_items)]
    return recs.to_dict(orient='records')
