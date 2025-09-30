from flask import Flask, jsonify, request, send_from_directory, send_file
import pymysql
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import time
from dotenv import load_dotenv
import hashlib
import gunicorn
import cloudinary
import cloudinary.uploader

from openpyxl import load_workbook
import io

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Configure CORS to allow POST requests
CORS(app, resources={
    r"/api/*": {
        "origins": "http://127.0.0.1:*",
        # "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# Database connection configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "port": int(os.getenv("DB_PORT")),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# Configuration       
cloudinary.config( 
    cloud_name = os.getenv("CL_CLOUD_NAME"),
    api_key = os.getenv("CL_API_KEY"), 
    api_secret = os.getenv("CL_API_SECRET"), # Click 'View API Keys' above to copy your API secret
    secure=True
)

# DB_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": "Eyobed579@papa",
#     "database": "organicdb",
# }

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # 30MB max file size

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data['username']
        password = data['password']
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        print(username, password, hashed_password)

        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                sql = """SELECT * FROM users WHERE username = %s AND password = %s"""
                cursor.execute(sql, (username, hashed_password))
                user = cursor.fetchone()
                usertype = user[4]
                print(usertype)
        
        if user:
            return jsonify({
                "message": "Login successful",
                'user_type': usertype
                }), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/get-profile', methods=['GET'])
def get_profile():
    pass


@app.route('/api/get-data', methods=['GET'])
def get_data():
    try:
        #time.sleep(10)
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
            'image_path': row[8],
            'catagory': row[9]} for row in rows]
        #print(result)
        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500


@app.route('/api/add-product', methods=['POST'])
def add_product():
    try:
        # # Check if image file was uploaded
        # if 'image-input' not in request.files:
        #     return jsonify({"error": "No image file provided"}), 400
        
        # file = request.files['image-input']
        # if file.filename == '':
        #     return jsonify({"error": "No selected file"}), 400
        
        # if not file or not allowed_file(file.filename):
        #     return jsonify({"error": "Invalid file type"}), 400
        
        # Save the image file
        
        # filename = secure_filename(file.filename)
        # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # file.save(file_path)
        
        # upload_result = cloudinary.uploader.upload(file)
        
        # Get form data with validation
        product_name = request.form.get('product-name-input')
        catagory = request.form.get('catagory')
        stock = request.form.get('quantity-input')
        unit = request.form.get('Unit')
        price = request.form.get('price-input')
        per = request.form.get('priceper')
        exdate = request.form.get('expirationDate-input')
        barcode = request.form.get('barcode')
        image_path = request.form.get('image-url')
        # image_path = f"/uploads/{filename}"
        # image_path = upload_result['secure_url']
        

        
        # Validate required fields
        if not all([product_name, stock, unit, price]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Database insertion
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                sql = """INSERT INTO product_list 
                        (product_name, stock, unit, price, per, exdate, barcode, image_path, catagory) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (product_name, stock, unit, price, per, exdate, barcode, image_path, catagory))
            connection.commit()
        
        return jsonify({
            "message": "Product added successfully",
            "product": {
                "product_name": product_name,
                "catagory": catagory,
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

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)




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
            # filename = secure_filename(file.filename)
            # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # file.save(file_path)

            upload_result = cloudinary.uploader.upload(file)
            image_path = upload_result['secure_url']

            # image_path = f"/uploads/{filename}"
            # print(image_path)
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
            WHERE product_id = %s
        """
        # print(query, values)
        # print(values) 
    
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
                cursor.execute("DELETE FROM product_list WHERE product_id = %s", (data['id'],))
            connection.commit()
            
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while deleting the product"}), 500


@app.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    try:
       
        for product in request.json:
            product_id = product['id']
            quantity = product['quantity']
            price = product['price']
            date = product['date']
        
            print(product_id, quantity, price, date)

            with pymysql.connect(**DB_CONFIG) as connection:
                with connection.cursor() as cursor:
                    sql = """INSERT INTO carts 
                            (product_id, quantity, price, date) 
                            VALUES (%s, %s, %s, %s)"""
                    cursor.execute(sql, (product_id, quantity, price, date))
                connection.commit()

            with pymysql.connect(**DB_CONFIG) as connection:
                with connection.cursor() as cursor:
                    sql2 = """UPDATE product_list
                            SET stock = stock - %s
                            WHERE product_id = %s;
                            """
                    cursor.execute(sql2, (quantity, product_id))
                connection.commit()


        # Get form data with validation
        # product_id = request.form.get('id')
        # quantity = request.form.get('quantity')
        # price = request.form.get('price')
        # date = request.form.get('date')
        
        # print(product_id, quantity, price, date)
        
        
        # Database insertion
        
        
        return jsonify({
            "message": "Product added successfully",
            "product": {
                "product_id": product_id,
                "quantity": quantity,
                "price": price,
                "date": date,
                
            }
        }), 201
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/get-history', methods=['GET'])
def get_history():
    try:
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute('''SELECT 
                                    carts.id AS cart_id, 
                                    product_list.product_name AS product_name, 
                                    product_list.image_path, 
                                    carts.quantity, 
                                    carts.price, 
                                    carts.date
                                FROM carts
                                JOIN product_list ON carts.product_id = product_list.product_id;
                                ''')
                rows = cursor.fetchall()
                #print(rows)
        result = [{
            'id': row[0],
            'product_name': row[1],
            'image_path': row[2],
            'quantity': row[3],
            'price': row[4],
            'date': row[5]} for row in rows]
        #print(result)
        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500


@app.route('/api/get-filter', methods=['GET'])
def get_filter():
    try:
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT catagory, unit, per FROM product_list")
                rows = cursor.fetchall()
                #print(rows)
        result = [{
            'catagory': row[0],
            'unit': row[1],
            'per': row[2]} for row in rows]
        # print(result)
        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500


@app.route('/api/get-user', methods=['GET'])
def getUser():
    try:
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                rows = cursor.fetchall()
        # print(rows)
        result = [{
            'id': row[0],
            'full_name': row[1],
            'username': row[2],
            'password': row[3],
            'role': row[4],
            'pp_url': row[5]} for row in rows]
        # print(result)
        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500


@app.route('/api/get-report', methods=['GET'])
def get_report():
    start = request.args.get('startDate')
    end = request.args.get('endDate')
    type = request.args.get('type')

    start_date= datetime.strptime(start, '%d-%m-%Y').date()
    end_date = datetime.strptime(end, '%d-%m-%Y').date()
    print(start_date, end_date, type)

    if not start or not end:
        return jsonify({"error": "Start and end dates are required"}), 400
    
    # return jsonify({"message": "Date is recived", "content": f'{start_date},{end_date}'}), 200



    try:
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute('''SELECT 
                                    carts.id AS cart_id, 
                                    product_list.product_name AS product_name, 
                                    product_list.image_path, 
                                    product_list.barcode,
                                    carts.quantity, 
                                    carts.price, 
                                    carts.date
                                    
                                FROM carts
                                JOIN product_list ON carts.product_id = product_list.product_id 
                                WHERE carts.date BETWEEN %s AND %s;
                                ''',(start_date, end_date))
                rows = cursor.fetchall()
                #print(rows)
        # filter= []
        # for product in rows:
        #     pdate= str(product[5])  # Assuming the date is in the 6th column
        #     product_date = datetime.strptime(pdate, '%Y-%m-%d').date()
        #     if (start_date <= product_date <= end_date):
        #         # rows.remove(product)
        #        filter.append(product)

       
        # filtered = filter.reverse()
        
        result = [{
            'id': row[0],
            'product_name': row[1],
            'barcode': row[3],
            'quantity': row[4],
            'price': row[5],
            'date': row[6]} for row in rows]
        #print(result)
        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500


@app.route('/api/get-inventory', methods=['GET'])
def get_inventory():
    try:
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM product_list")
                rows = cursor.fetchall()
                # print(rows)
       
       
        result = [{
            
            'product_name': row[1],
            'stock': row[2],
            'unit': row[3],
            'price': row[4],
            'per': row[5],
            'exdate': row[6],
            'barcode': row[7],
            
            'catagory': row[9]} for row in rows]
        #print(result)
        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500


@app.route('/download-excel', methods=['POST'])
def download_excel():
    products = request.json.get('products')  # receive JSON array of objects

    # Load your Excel template
    template_path = 'templates/template.xlsx'
    wb = load_workbook(template_path)
    ws = wb.active

    # Define the column order you want in Excel
    headers = ["Barcode", "Category", "Product Name", "Price", "Stock", "Unit", "Per", "Expiry Date"]
    
    # Optional: write headers if your template doesn't have them
    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header)

    # Start writing data from row 2
    for row_num, product in enumerate(products, start=2):
        ws.cell(row=row_num, column=1, value=product['barcode'])
        ws.cell(row=row_num, column=2, value=product['catagory'])
        ws.cell(row=row_num, column=3, value=product['product_name'])
        ws.cell(row=row_num, column=4, value=float(product['price']))
        ws.cell(row=row_num, column=5, value=product['stock'])
        ws.cell(row=row_num, column=6, value=product['unit'])
        ws.cell(row=row_num, column=7, value=product['per'])
        
        # Format expiry date
        try:
            date_obj = datetime.strptime(product['exdate'], "%a, %d %b %Y %H:%M:%S %Z")
            ws.cell(row=row_num, column=8, value=date_obj.strftime("%d %b %Y"))
        except:
            ws.cell(row=row_num, column=8, value=product['exdate'])  # fallback

    # Send the workbook as a downloadable file
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="product_inventory.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )



if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
