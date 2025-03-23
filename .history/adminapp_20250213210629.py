from flask import Flask, jsonify, request, send_from_directory
import pymysql
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Configure CORS to allow POST requests
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Eyobed579@papa",
    "database": "organicdb"
}

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # 30MB max file size

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/get-data', methods=['GET'])
def get_data():
    try:
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM product_list")
                rows = cursor.fetchall()
                #print(rows)
        result = [{
            'id': row[0],
            'product_name': row[1],
            'stock': row[2],
            'unit': row[3],
            'price': row[4],
            'per': row[5],
            'exdate': row[6],
            'barcode': row[7],
            'image_path': row[8]} for row in rows]
        #print(result)
        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500



@app.route('/api/add-product', methods=['POST'])
def add_product():
    try:
        # Check if image file was uploaded
        if 'image-input' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image-input']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
        
        # Save the image file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Get form data with validation
        product_name = request.form.get('product-name-input')
        stock = request.form.get('quantity-input')
        unit = request.form.get('Unit')
        price = request.form.get('price-input')
        per = request.form.get('priceper')
        exdate = request.form.get('expirationDate-input')
        barcode = request.form.get('barcode')
        image_path = f"/uploads/{filename}"
        
        # Validate required fields
        if not all([product_name, stock, unit, price]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Database insertion
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                sql = """INSERT INTO product_list 
                        (product_name, stock, unit, price, per, exdate, barcode, image_path) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (product_name, stock, unit, price, per, exdate, barcode, image_path))
            connection.commit()
        
        return jsonify({
            "message": "Product added successfully",
            "product": {
                "product_name": product_name,
                "stock": stock,
                "unit": unit,
                "price": price,
                "per": per,
                "exdate": exdate,
                "barcode": barcode,
                "image_path": image_path
            }
        }), 201
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)




@app.route('/api/update-product', methods=['POST'])
def update_product():
    try:
        data = request.form  # Use request.form for FormData
        product_id = data.get('id')
        fields = {}
        file = None
        
        if 'image-input' not in request.files:
            pass
        else:
            file = request.files['image-input']

            # Check if image file was uploaded
        if file == None:
            print("No image file provided")
            pass

        elif file.filename == '':
            return jsonify({"error": "No selected file"}), 400
    
        elif not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
        
        else:
            # Save the image file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            image_path = f"/uploads/{filename}"
            print(image_path)
            fields.update({"image_path": image_path})
    
        
        
        # Validate required fields
        if not product_id :
            return jsonify({"success": False, "error": "Missing required fields (product ID)"}), 400
        else:
            for key, value in data.items():
                if value == "" or key == "id":
                    continue
                else:
                    fields.update({key: value})
               
        set_clause = ", ".join([f"{key} = %s" for key in fields.keys()])
        values = list(fields.values())  # Extract the values to bind
        values.append(product_id)  # Add the product_id for the WHERE clause

    # Construct the query
        query = f"""
            UPDATE product_list 
            SET {set_clause} 
            WHERE id = %s
        """
        print(query, values)
        print(values)
    
        # Database update logic
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
            connection.commit()

        return jsonify({"success": True, "message": "Product updated successfully"}), 200

    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return jsonify({"success": False, "error": "An error occurred while updating the product"}), 500




@app.route('/api/delete-product', methods=['DELETE'])
def delete_product():
    data = request.json
    try:
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM product_list WHERE id = %s", (data['id'],))
            connection.commit()
            
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while deleting the product"}), 500

# Route to handle the API request for adding items
# @app.route('/api/add_item', methods=['POST'])
# def add_item():
#     data = request.json  # Get JSON data from request body
#     print(data)  # Print the received data to the console for testing

#     # Return a success message with the received data
#     return jsonify({"message": "Data received successfully", "data": data}), 200

# @app.route('/api/upload-image', methods=['POST'])
# def upload_image():
#     if 'image' not in request.files:
#         return jsonify({"success": False, "error": "No file part"}), 400

#     file = request.files['image']

#     if file.filename == '':
#         return jsonify({"success": False, "error": "No selected file"}), 400

#     if file:
#         # Save the file to the specified directory
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(file_path)

#         # Return the path of the saved image
#         return jsonify({"success": True, "image_path": file_path}), 200

#     return jsonify({"success": False, "error": "File upload failed"}), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host="0.0.0.0", debug=True)
