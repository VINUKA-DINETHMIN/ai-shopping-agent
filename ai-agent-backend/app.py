from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

def scrape_products(product_type):
    # Construct the URL for the product listings based on the product type
    url = f'https://www.ebay.com/sch/i.html?_nkw={product_type}'
    
    # Send a GET request to the website
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to retrieve the page.")
        return []
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract product information (adjust the selectors based on the website structure)
    products = []
    listings = soup.select('.s-item')  # Example selector for eBay listings
    
    for listing in listings:
        # Extract product name
        name = listing.select_one('.s-item__title')
        if name:
            name = name.text.strip()
        else:
            continue
        
        # Extract product price
        price = listing.select_one('.s-item__price')
        if price:
            price = price.text.strip().replace('$', '').replace(',', '')
        else:
            continue
        
        # Add product to the list
        try:
            price = float(price)
            products.append({"name": name, "price": price})
        except ValueError:
            continue  # Skip products with invalid price format
    
    return products

@app.route("/api/auth/recommend", methods=["POST"])
def recommend():
    try:
        data = request.json
        budget = float(data.get("budget", 0))
        product_type = data.get("product", "").lower()

        # Scrape products based on the requested product type
        products = scrape_products(product_type)

        # Filter products within the budget
        recommendations = [
            product for product in products if product["price"] <= budget
        ]

        # Log recommendations for debugging
        print(f"Recommendations: {recommendations}")

        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
