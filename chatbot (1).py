# -*- coding: utf-8 -*-
"""ChatBot.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1noNPFbjpV5Vvwbke8sCn00Gq5zOrTu-5
"""

!ngrok authtoken 2mxVFSwfJ4fCN76oELdPFKCLtat_2N8w5Jqei2NJnjZPrm453



# Install required libraries
!pip install openai flask vaderSentiment pyngrok

import openai
from flask import Flask, request, jsonify
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pyngrok import ngrok
from threading import Thread

# Initialize Flask app
app = Flask(__name__)

# Initialize Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

# Define OpenAI API key (replace with your actual key)
openai.api_key = 'replaced key'  # Use your actual API key here

# Set initial product price range
MIN_PRICE = 50
MAX_PRICE = 150
BOT_PRICE = 70  # Initial price offered by the bot

# Endpoint to start negotiation
@app.route('/negotiate', methods=['POST'])
def negotiate():
    data = request.json
    user_message = data.get('message')
    user_offer = int(data.get('offer', 0))  # User's offered price

    # Analyze sentiment of user message
    sentiment_score = analyzer.polarity_scores(user_message)['compound']

    # Adjust bot's price based on sentiment score (polite users get a discount)
    sentiment_discount = 0
    if sentiment_score > 0.7:  # Positive sentiment
        sentiment_discount = 15

    # Logic for price negotiation
    bot_price = BOT_PRICE - sentiment_discount

    if user_offer >= bot_price:
        response = f"Your offer of {user_offer} is  accepted! So the price is {user_offer} "
        return jsonify({"response": response, "final_price": user_offer})

    elif user_offer < MIN_PRICE:
        response = f"Your offer is too low. The minimum price is {MIN_PRICE}."
        return jsonify({"response": response, "counteroffer": MIN_PRICE})

    elif user_offer < bot_price:
        counteroffer = (user_offer + bot_price) // 2
        response = f"Your offer is below my price. How about we settle at {counteroffer}?"
        return jsonify({"response": response, "counteroffer": counteroffer})

    else:
        response = f"I can offer you a price of {bot_price}."
        return jsonify({"response": response, "counteroffer": bot_price})

# Endpoint to continue negotiation
@app.route('/counteroffer', methods=['POST'])
def counter_offer():
    data = request.json
    user_counteroffer = int(data.get('counteroffer'))

    if user_counteroffer >= MIN_PRICE:
        response = f"Your counteroffer of {user_counteroffer} is accepted."
        return jsonify({"response": response, "final_price": user_counteroffer})
    else:
        response = f"Your counteroffer is too low. The minimum I can accept is {MIN_PRICE}."
        return jsonify({"response": response, "counteroffer": MIN_PRICE})

# Function to run Flask app
def run_flask():
    app.run(port=5000)

# Start Flask app in a separate thread
flask_thread = Thread(target=run_flask)
flask_thread.start()

# Start ngrok tunnel
public_url = ngrok.connect(5000)
print(f"Public URL: {public_url}")

!curl -X POST https://85d3-35-192-93-66.ngrok-free.app/negotiate \
     -H 'Content-Type: application/json' \
     -d '{"message": "I would like a better price.", "offer": 25}'

!curl -X POST https://85d3-35-192-93-66.ngrok-free.app/negotiate \
     -H 'Content-Type: application/json' \
     -d '{"message": "I would like a better price.", "offer": 55}'

!curl -X POST https://85d3-35-192-93-66.ngrok-free.app/negotiate \
     -H 'Content-Type: application/json' \
     -d '{"message": "I would like a better price.", "offer": 1000}'