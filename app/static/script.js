let products = [
    {id: 1, name: "Apple iPhone 12"},
    {id: 2, name: "Samsung Galaxy S21"},
    {id: 3, name: "Laptop Bag"},
    {id: 4, name: "Wireless Mouse"},
    {id: 5, name: "HDMI Cable"}
];

let cart = [];

function renderProducts() {
    const div = document.getElementById("products");
    products.forEach(p => {
        div.innerHTML += `<button onclick="addToCart(${p.id})">${p.name}</button><br/>`;
    });
}

function addToCart(id) {
    if (!cart.includes(id)) {
        cart.push(id);
        document.getElementById("cart").innerHTML += `<li>${products.find(p => p.id === id).name}</li>`;
    }
}

function getRecommendations() {
    fetch("/recommend", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({cart})
    }).then(res => res.json())
      .then(data => {
        const rec = document.getElementById("recommendations");
        rec.innerHTML = "";
        data.forEach(p => {
            rec.innerHTML += `<li>${p.product_name}</li>`;
        });
    });
}

renderProducts();
