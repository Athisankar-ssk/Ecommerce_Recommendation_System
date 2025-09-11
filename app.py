from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask import request
from models import db, User, Product
import recommender

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'e3f6a11f3b57eac673c6f9de854b5201'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    CORS(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/')
    def home():
        if current_user.is_authenticated:
            # User is logged in, redirect to catalog
            return redirect(url_for('catalog'))
            # Otherwise show public home page with login/register
        return render_template('home.html')


    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            if User.query.filter_by(email=email).first():
                flash('Email already registered')
                return redirect(url_for('register'))
            new_user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please login.')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('catalog'))
            flash('Invalid credentials')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/catalog')
    @login_required
    def catalog():
        # Get page number and department filter from URL params
        page = request.args.get('page', 1, type=int)
        per_page = 12  # Products per page
        department = request.args.get('department', None)

        # Query for products
        query = Product.query
        if department:
            query = query.filter_by(department=department)
        products = query.paginate(page=page, per_page=per_page, error_out=False)

        # Get all distinct departments for dropdown filter
        categories = Product.query.with_entities(Product.department).distinct().all()

        # Personalized recommendations for logged-in user
        recs_ids = recommender.recommend_als_safe(current_user.id, N=5)
        recommendations = Product.query.filter(Product.product_id.in_(recs_ids)).all()

        return render_template(
            'catalog.html',
            products=products,
            recommendations=recommendations,
            categories=categories
        )

    @app.route('/product/<int:product_id>')
    @login_required
    def product_detail(product_id):
        product = Product.query.filter_by(product_id=product_id).first_or_404()
        similar_ids = recommender.recommend_content(product_id, N=5)
        similar_products = Product.query.filter(Product.product_id.in_(similar_ids)).all()
        return render_template('product.html', product=product, similar=similar_products)

    @app.route('/api/recommend/user/<int:user_id>')
    @login_required
    def api_user_recommend(user_id):
        rec_ids = recommender.recommend_als_safe(user_id, N=5)
        recs = Product.query.filter(Product.product_id.in_(rec_ids)).all()
        return jsonify([{'product_id': p.product_id, 'product_name': p.product_name} for p in recs])

    @app.route('/api/recommend/product/<int:product_id>')
    @login_required
    def api_product_recommend(product_id):
        sim_ids = recommender.recommend_content(product_id, N=5)
        sims = Product.query.filter(Product.product_id.in_(sim_ids)).all()
        return jsonify([{'product_id': p.product_id, 'product_name': p.product_name} for p in sims])

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
