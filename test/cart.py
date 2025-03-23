from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="organicdb"
)
cursor = conn.cursor()

@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    data = request.json
    product_id = data.get("product_id")
    weight = data.get("weight")  # weight in grams

    if not product_id or not weight:
        return jsonify({"message": "Invalid input"}), 400
    
    # Fetch price per 100g
    cursor.execute("SELECT price_per_100g FROM products WHERE id = %s", (product_id,))
    result = cursor.fetchone()
    if not result:
        return jsonify({"message": "Product not found"}), 404
    
    price_per_100g = result[0]
    total_price = (weight / 100) * price_per_100g
    
    # Insert into cart
    cursor.execute("INSERT INTO cart (product_id, weight, total_price) VALUES (%s, %s, %s)", 
                   (product_id, weight, total_price))
    conn.commit()
    
    return jsonify({"message": "Item added to cart", "total_price": total_price}), 200

if __name__ == "__main__":
    app.run(debug=True)
