from flask import Flask, jsonify
from flask_cors import CORS
import plotly.express as px
import pandas as pd

app = Flask(__name__)
# Configure CORS to allow POST requests
CORS(app, resources={
    r"/*": {
        "origins": "http://127.0.0.1:5502",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# @app.route('/chart-data', methods=['GET'])
# def chart_data():
#     df = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [10, 20, 25, 30]})
#     fig = px.line(df, x='x', y='y', title="Interactive Chart")
#     return jsonify(fig.to_json())

# @app.route('/inventory-chart')
# def inventory_chart():
#     # Sample inventory data
#     data = {
#         'Category': ['Laptops', 'Phones', 'Tablets', 'Accessories'],
#         'Stock': [600, 300, 120, 200]
#     }

#     df = pd.DataFrame(data)

#     # Create a bar chart with Plotly
#     fig = px.bar(df, x='Category', y='Stock', title="Inventory Stock Levels", 
#                  labels={'Stock': 'Stock Quantity', 'Category': 'Item Category'})

#     return jsonify(fig.to_json())  # Convert to JSON for frontend rendering


@app.route('/stock-trend')
def stock_trend():
  

    # Sample Data (Replace with actual DataFrame)
    data = {
        "Date": ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"],
        "Stock": [500, 450, 480, 460]
    }

    df = pd.DataFrame(data)

    # Convert Date Column to Proper Format
    df["Date"] = pd.to_datetime(df["Date"])

    # Reset Index (Avoid Index Being Misinterpreted)
    df = df.reset_index(drop=True)

    # Plot Graph
    fig = px.line(df, x="Date", y="Stock", title="Stock Trend Over Time")
    #fig.show()

    return jsonify(fig.to_json())


if __name__ == '__main__':
    app.run(debug=True)
