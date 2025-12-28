from flask import Flask, render_template, request, jsonify
import json
import random
from datetime import datetime

app = Flask(__name__)

# Load food data
with open('food_data.json', 'r', encoding='utf-8') as f:
    food_data = json.load(f)

def get_recommendations(preferences):
    """Get food recommendations based on user preferences"""
    all_foods = food_data['foods']
    filtered_foods = []
    
    # Filter based on preferences
    for food in all_foods:
        match = True
        
        # Category filter
        if preferences.get('category') and preferences['category'] != 'Any':
            if food['category'] != preferences['category']:
                match = False
        
        # Price filter
        if preferences.get('price_range'):
            if preferences['price_range'] == 'Low' and food['price_range'] != '₹30-50':
                match = False
            elif preferences['price_range'] == 'Medium' and food['price_range'] not in ['₹40-60', '₹50-100']:
                match = False
            elif preferences['price_range'] == 'High' and food['price_range'] not in ['₹80-150', '₹120-180']:
                match = False
        
        # Time-based recommendation
        current_hour = datetime.now().hour
        if current_hour < 12:
            best_time = 'Breakfast'
        elif current_hour < 17:
            best_time = 'Lunch'
        else:
            best_time = 'Evening'
        
        # Give priority to foods that are best at current time
        if best_time in food['best_time']:
            food['priority'] = 10
        else:
            food['priority'] = 5
        
        if match:
            filtered_foods.append(food)
    
    # Sort by priority and rating
    filtered_foods.sort(key=lambda x: (x.get('priority', 0), x['rating']), reverse=True)
    
    # Return top 3 recommendations
    return filtered_foods[:3]

def get_random_tip():
    """Get random food tip from Kiro context"""
    tips = [
        "Pro Tip: Try Golgappe with both sweet and spicy water!",
        "Hot weather? Lassi is your best friend!",
        "Visit Chandni Chowk for authentic street food experience",
        "Evening time is best for Chaat and snacks",
        "For quick bite, try Aloo Tikki - ready in minutes!"
    ]
    return random.choice(tips)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        preferences = {
            'category': data.get('category', 'Any'),
            'price_range': data.get('price_range', 'Any')
        }
        
        recommendations = get_recommendations(preferences)
        tip = get_random_tip()
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'tip': tip,
            'count': len(recommendations)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/foods')
def get_all_foods():
    return jsonify(food_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
