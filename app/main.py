from flask import Flask, request, jsonify, render_template
from recommender import get_recommendations

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    cart = request.json.get("cart", [])
    recommendations = get_recommendations(cart)
    return jsonify(recommendations)

if __name__ == "__main__":
    app.run(debug=True)
