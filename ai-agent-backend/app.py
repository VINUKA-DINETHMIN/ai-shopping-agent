from flask import Flask, request, jsonify
from flask_cors import CORS  # type: ignore
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains by default

def scrape_products(product_type):
    # Construct the URL for the product listings based on the product type
    url = f'https://www.ebay.com/s?k={product_type}'  # Example URL, adjust for real scraping
    
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
    
    # Example: Find all product containers (adjust the class name or tag)
    product_containers = soup.find_all('li', class_='s-item')  # Adjust the selector for eBay
    
    for container in product_containers:
        # Extract product name (adjust the selector)
        name = container.find('h3', class_='s-item__title')
        if name:
            name = name.text.strip()
        else:
            continue
        
        # Extract product price (adjust the selector)
        price = container.find('span', class_='s-item__price')
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

@app.route("/api/auth/recommend", methods=["POST"])  # Adjusted URL
def recommend():
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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
