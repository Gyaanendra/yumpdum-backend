# api/index.py
from flask import Flask, jsonify, request
import json
import os
from pathlib import Path

app = Flask(__name__)

# Load the restaurant data - adjust the path for Vercel
# In Vercel, the working directory is different
base_dir = Path(__file__).resolve().parent.parent
json_path = base_dir / "restaurants_data.json"

try:
    with open(json_path, 'r') as file:
        restaurants = json.load(file)
except FileNotFoundError:
    # Fallback - try loading from the api directory
    try:
        with open(Path(__file__).resolve().parent / "restaurants_data.json", 'r') as file:
            restaurants = json.load(file)
    except FileNotFoundError:
        restaurants = []  # Default empty list if file not found

# Helper function to find a restaurant by ID
def find_restaurant(restaurant_id):
    for restaurant in restaurants:
        if restaurant['restaurant_id'] == restaurant_id:
            return restaurant
    return None

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome to the Restaurant API",
        "endpoints": [
            "/api/restaurants",
            "/api/restaurants/{id}",
            "/api/restaurants/{id}/reviews",
            "/api/restaurants/{id}/menu",
            "/api/restaurants/search?q={query}"
        ]
    })

# Route to get all restaurants
@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    name_filter = request.args.get('name')
    
    if name_filter:
        filtered_restaurants = [r for r in restaurants if name_filter.lower() in r['name'].lower()]
        return jsonify(filtered_restaurants)
    
    return jsonify(restaurants)

# Route to get a specific restaurant by ID
@app.route('/api/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    restaurant = find_restaurant(restaurant_id)
    if restaurant:
        return jsonify(restaurant)
    return jsonify({"error": "Restaurant not found"}), 404

# Route to get reviews for a specific restaurant
@app.route('/api/restaurants/<int:restaurant_id>/reviews', methods=['GET'])
def get_restaurant_reviews(restaurant_id):
    restaurant = find_restaurant(restaurant_id)
    if restaurant:
        return jsonify(restaurant['user_reviews'])
    return jsonify({"error": "Restaurant not found"}), 404

# Route to get menu items for a specific restaurant
@app.route('/api/restaurants/<int:restaurant_id>/menu', methods=['GET'])
def get_restaurant_menu(restaurant_id):
    restaurant = find_restaurant(restaurant_id)
    if restaurant and 'order' in restaurant and 'menu_items' in restaurant['order']:
        return jsonify(restaurant['order']['menu_items'])
    return jsonify({"error": "Restaurant or menu not found"}), 404

# Route to search restaurants by keyword (in name or description)
@app.route('/api/restaurants/search', methods=['GET'])
def search_restaurants():
    keyword = request.args.get('q', '')
    if not keyword:
        return jsonify({"error": "Search query parameter 'q' is required"}), 400
    
    results = [r for r in restaurants if 
              keyword.lower() in r['name'].lower() or 
              keyword.lower() in r['description'].lower()]
    
    return jsonify(results)

# For local testing
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)