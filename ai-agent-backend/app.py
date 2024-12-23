import spacy
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
from forex_python.converter import CurrencyRates
import speech_recognition as sr

# Load the NLP model
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
CORS(app)

# Extract keywords from the product type using NLP
def extract_keywords(text):
    doc = nlp(text)
    keywords = []
    for token in doc:
        if token.pos_ in ['NOUN', 'ADJ']:  # Extract nouns and adjectives
            keywords.append(token.text.lower())
    return " ".join(keywords)

# Scrape products from eBay or Walmart based on the product type
def scrape_products(product_type, site):
    if site == "ebay":
        url = f'https://www.ebay.com/sch/i.html?_nkw={product_type}'
    elif site == "walmart":
        url = f'https://www.walmart.com/search/?query={product_type}'
    else:
        return []

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the page from {site}.")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    products = []

    if site == "ebay":
        listings = soup.select('.s-item')
        for listing in listings:
            name = listing.select_one('.s-item__title')
            price = listing.select_one('.s-item__price')
            link = listing.select_one('.s-item__link')
            if name and price and link:
                try:
                    price_value = float(price.text.strip().replace('$', '').replace(',', ''))
                    products.append({
                        "name": name.text.strip(),
                        "price": price_value,
                        "url": link['href']
                    })
                except ValueError:
                    continue

    elif site == "walmart":
        listings = soup.select('.search-result-gridview-item')
        for listing in listings:
            name = listing.select_one('.product-title-link')
            price = listing.select_one('.price-main .visuallyhidden')
            link = listing.select_one('.product-title-link')
            if name and price and link:
                try:
                    price_value = float(price.text.strip().replace('$', '').replace(',', ''))
                    products.append({
                        "name": name.text.strip(),
                        "price": price_value,
                        "url": f"https://www.walmart.com{link['href']}"
                    })
                except ValueError:
                    continue

    return products

# Convert currency using forex-python
def convert_currency(amount, from_currency, to_currency):
    cr = CurrencyRates()
    return cr.convert(from_currency, to_currency, amount)

# Voice command recognition function
def recognize_voice_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for a command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            command = recognizer.recognize_google(audio)
            print(f"Command recognized: {command}")
            return command
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            print("Sorry, the speech recognition service is unavailable.")
            return None

# API endpoint to get product recommendations
@app.route("/api/auth/recommend", methods=["POST"])
def recommend():
    try:
        data = request.json
        budget = float(data.get("budget", 0))
        product_type = data.get("product", "").lower()
        use_nlp = data.get("use_nlp", False)
        currency = data.get("currency", "USD")
        language = data.get("language", "en")

        if use_nlp:
            product_type = extract_keywords(product_type)  # Process the product type with NLP

        ebay_products = scrape_products(product_type, "ebay")
        walmart_products = scrape_products(product_type, "walmart")

        all_products = ebay_products + walmart_products
        recommendations = [
            product for product in all_products if product["price"] <= budget
        ]

        # Convert prices based on the selected currency
        for product in recommendations:
            product["price"] = convert_currency(product["price"], "USD", currency)

        recommendations = sorted(recommendations, key=lambda x: x['price'])

        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# API endpoint for voice search
@app.route("/api/auth/voice_search", methods=["GET"])
def voice_search():
    try:
        command = recognize_voice_command()
        if command:
            # Use the voice command as the product type
            data = {
                "product": command,
                "budget": 100,  # Default budget
                "use_nlp": True,  # Use NLP for processing
                "currency": "USD",
                "language": "en"
            }
            # Call the recommend endpoint with the voice command
            response = recommend()
            return response
        else:
            return jsonify({"error": "No valid voice command recognized."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
