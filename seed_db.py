from models import db, Product
from app import create_app
import pandas as pd

app = create_app()

def seed_products():
    with app.app_context():
        db.create_all()
        df = pd.read_csv("products_cleaned.csv")
        for _, row in df.iterrows():
            if not Product.query.filter_by(product_id=row['product_id']).first():
                product = Product(
                    product_id=row['product_id'],
                    product_name=row['product_name'],
                    aisle=row.get('aisle', ''),
                    department=row.get('department', '')
                )
                db.session.add(product)
        db.session.commit()
        print("Seeded products.")

if __name__ == "__main__":
    seed_products()
