import json
from flask import Flask, jsonify, request, send_from_directory, send_file, session, redirect, url_for
import pymysql
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import time
from dotenv import load_dotenv
import hashlib
import gunicorn
from functools import wraps
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.exceptions import NotFound


from openpyxl import load_workbook
import io

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Configure CORS to allow POST requests
CORS(app, supports_credentials=True, resources={
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
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            # If it's an API / AJAX call → return JSON
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({"error": "Unauthorized, please log in"}), 401

            # Otherwise → redirect to login page
            return redirect(url_for("start"))
        return f(*args, **kwargs)
    return decorated_function




@app.route('/api/login', methods=['POST'])
def login():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        # with pymysql.connect(**DB_CONFIG) as connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "message": "User not found."})

        stored_password = user[3]
        if hashed_password != stored_password:
            return jsonify({"success": False, "message": "Incorrect password."})

        # If login is successful
        user_id = user[0]
        full_name = user[1]
        user_type = user[4]
        url = user[5]
        status = user[6]

        if status =='Disabled':
            return jsonify({"success": False, "message": "Your account has been Disabled. Please Contact the admin."})
        
        else:
            session.permanent = True
            session['id'] = user_id
            session['username'] = username
            session['full_name'] = full_name
            session['user_type'] = user_type
            session['pp_url'] = url

            if user_type == "admin":
                redirect_url = url_for('Home')
            else:
                redirect_url = url_for('Home')

            return jsonify({"success": True, "redirect": redirect_url})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

    finally:
        connection.close()


@app.route('/logout')
@login_required
def logout():
    # Clear all session data
    session.clear()
    return redirect(url_for('start'))

@app.route('/<path:path>')
# @login_required
def serve_file(path):
    return send_from_directory('.', path)

# @app.route('/<path:path>')
# # @login_required
# def serve_dashboard(path):
#     return send_from_directory('Dashboard', path)

######################## Navigation ######################################

@app.route('/', methods=['GET'])
def start():
    return send_from_directory('.','login.html' )

@app.route('/Home', methods=['GET'])
@login_required
def Home():
    return send_from_directory('.', 'admincursor.html')

@app.route('/Cart', methods=['GET'])
@login_required
def Cart():
    return send_from_directory('Cart', 'index.html')

@app.route('/Profile', methods=['GET'])
@login_required
def Profile():
    return send_from_directory('.', 'profile.html')

@app.route('/Dashboard', methods=['GET'])
@login_required
def Dashboard():
    return send_from_directory('Dashboard', 'index.html')

@app.route('/dashboard', methods=['GET'])
# @login_required
def dashboard():
    return send_from_directory('Dashboard', 'dashboard.html')

@app.route('/accounts', methods=['GET'])
# @login_required
def accounts():
    return send_from_directory('Dashboard', 'accounts.html')

@app.route('/reports', methods=['GET'])
# @login_required
def reports():
    return send_from_directory('Dashboard', 'reports.html')

@app.route('/sales', methods=['GET'])
# @login_required
def sales():
    return send_from_directory('Dashboard', 'sales.html')

@app.route('/history', methods=['GET'])
# @login_required
def history():
    return send_from_directory('Dashboard', 'history.html')

@app.route('/charts', methods=['GET'])
# @login_required
def charts():
    return send_from_directory('Dashboard', 'charts.html')
    

@app.route('/help', methods=['GET'])
# @login_required
def help():
    return send_from_directory('Dashboard', 'help.html')



@app.route('/api/get-profile', methods=['GET'])
@login_required
def get_profile():
    return jsonify({
        'user_id': session['id'],
        'username':session['username'],
        'full_name' : session['full_name'],
         'user_type' :  session['user_type'],
         'pp_url': session['pp_url']
    })

@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    user_id = request.form.get('user_id')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # print(user_id, old_password, new_password, confirm_password)
    if not all([user_id, old_password, new_password, confirm_password]):
        return jsonify({"error": "Missing required fields",
                        "message": "Missing required fields"}), 400

    hashed_old_password = hashlib.md5(old_password.encode()).hexdigest()
    hashed_new_password = hashlib.md5(new_password.encode()).hexdigest()
    hashed_confirm_password = hashlib.md5(confirm_password.encode()).hexdigest()

   
    if hashed_new_password != hashed_confirm_password:
        return jsonify({"error": "New password and confirm password do not match",
                        "message": "New password and confirm password do not match"}), 400
    
    connection = pymysql.connect(**DB_CONFIG)
    try:
        # with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                if user:
                    if user[3] != hashed_old_password:
                        return jsonify({"error": "Old password is incorrect",
                                        "message": "Old password is incorrect"}), 400
                    else:
                        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_new_password, user_id))
                        connection.commit()
                        return jsonify({"message": "Password changed successfully"}), 200
                else:
                    return jsonify({"error": "User not found",
                                    "message": "User not found"}), 400
    finally:
        connection.close()   
    # with pymysql.connect(**DB_CONFIG) as connection:
    #     with connection.cursor() as cursor:
    #         cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user_id))
    #     connection.commit()
    
    # return jsonify({"message": "Password changed successfully"}), 200
    
    # except Exception as e:
    # except Exception as e:
    #     print(f"Error: {e}")
    #     return jsonify({"error": "An error occurred while changing the password"}), 500
    
@app.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    user_id = request.form.get('id')
    userName = request.form.get('username')
    fullName = request.form.get('full_name')

    fields = {}
    image_path = None

    # --------------------------
    # 1️⃣ Check for uploaded file
    # --------------------------
    if 'fileInput' in request.files:
        file = request.files['fileInput']

        if file and file.filename != '' and allowed_file(file.filename):
           
            image_path = upload_or_get_cloudinary_url(file, "profiles")

            # update image path in fields for DB
            fields.update({"profile_picture_url": image_path})

        else:
            return jsonify({"error": "Invalid or missing file"}), 400

    # --------------------------------
    # 2️⃣ Validate other form fields
    # --------------------------------
    if not user_id:
        return jsonify({"success": False, "error": "Missing required field: user_id"}), 400
    else:
        for key, value in request.form.items():
            if value == "" or key == "id":
                continue
            else:
                fields.update({key: value})

    if not fields:
        return jsonify({"error": "No valid fields to update"}), 400

    # --------------------------------
    # 3️⃣ Build SQL update statement
    # --------------------------------
    set_clause = ", ".join([f"{key} = %s" for key in fields.keys()])
    values = list(fields.values())
    values.append(user_id)

    query = f"UPDATE users SET {set_clause} WHERE id = %s"

    # --------------------------------
    # 4️⃣ Execute SQL update
    # --------------------------------
    connection = pymysql.connect(**DB_CONFIG)
    try:    
        # with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
            connection.commit()
    finally:
        connection.close()    
    # --------------------------------
    # 5️⃣ Update session variables
    # --------------------------------
    session['username'] = userName
    session['full_name'] = fullName
    if image_path:
        session['pp_url'] = image_path

    return jsonify({"success": True, "message": "Profile Updated Successfully"}), 200




def upload_or_get_cloudinary_url(file, folder):
    """
    Uploads a file to Cloudinary if not already present in the given folder.
    Returns the file's secure URL.

    Parameters:
        file (FileStorage): The uploaded file (e.g., from request.files['file']).
        folder (str): Cloudinary folder to upload into (default: "shared_uploads").

    Returns:
        str: The secure URL of the image on Cloudinary.
    """
    # ✅ Extract filename without extension
    filename = os.path.splitext(file.filename)[0]
    public_id = f"{folder}/{filename}"  # Used to check duplicates properly

    try:
        # ✅ Check if already uploaded (must match full folder path)
        existing = cloudinary.api.resource(public_id)
        print(f"✅ Image already exists: {existing['secure_url']}")
        return existing['secure_url']

    except NotFound:
        # 🔄 Upload new image into the correct folder
        print(f"🔄 Uploading new image to folder '{folder}'...")
        upload_result = cloudinary.uploader.upload(
            file,
            folder=folder,            # ✅ ensures it shows up in that folder
            public_id=filename,       # ✅ prevents duplicate subfolder naming
            overwrite=False,          # ❌ don’t overwrite existing files
            unique_filename=False     # ❌ don’t add random characters
        )
        print(f"✅ Uploaded new image: {upload_result['secure_url']}")
        return upload_result['secure_url']

@app.route('/api/get-data', methods=['GET'])
@login_required
def get_data():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        #time.sleep(10)
        # with pymysql.connect(**DB_CONFIG) as connection:
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

    finally:
        connection.close()

@app.route('/api/add-product', methods=['POST'])
@login_required
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
        
        # filename = secure_filename(file.filename)
        # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # file.save(file_path)
        
        image_path = upload_or_get_cloudinary_url(file, "uploads")
        
        # Get form data with validation
        product_name = request.form.get('product-name-input')
        catagory = request.form.get('catagory')
        stock = request.form.get('quantity-input')
        unit = request.form.get('Unit')
        price = request.form.get('price-input')
        per = request.form.get('priceper')
        exdate = request.form.get('expirationDate-input')
        barcode = request.form.get('barcode')
        # image_path = request.form.get('image-url')
        # image_path = f"/uploads/{filename}"
        # image_path = upload_result['secure_url']
        

        
        # Validate required fields
        if not all([product_name, stock, unit, price]):
            return jsonify({"error": "Missing required fields"}), 400
        connection = pymysql.connect(**DB_CONFIG)
        try:    
            # Database insertion
            # with pymysql.connect(**DB_CONFIG) as connection:
                with connection.cursor() as cursor:
                    sql = """INSERT INTO product_list 
                            (product_name, stock, unit, price, per, exdate, barcode, image_path, catagory) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (product_name, stock, unit, price, per, exdate, barcode, image_path, catagory))
                connection.commit()
        finally:
            connection.close()
            
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
@login_required
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

            image_path = upload_or_get_cloudinary_url(file, "uploads")

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
        connection = pymysql.connect(**DB_CONFIG)
        try:
            # Database update logic
            # with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
            connection.commit()
        finally:
            connection.close()

        return jsonify({"success": True, "message": "Product updated successfully"}), 200

    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return jsonify({"success": False, "error": "An error occurred while updating the product"}), 500


@app.route('/api/delete-product', methods=['DELETE'])
@login_required
def delete_product():
    data = request.json
    connection = pymysql.connect(**DB_CONFIG)
    try:
        # with pymysql.connect(**DB_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM product_list WHERE product_id = %s", (data['id'],))
        connection.commit()
            
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while deleting the product"}), 500
    finally:
        connection.close()

@app.route('/api/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    connection = pymysql.connect(**DB_CONFIG)
    try:
       
        for product in request.json:
            product_id = product['id']
            quantity = product['quantity']
            price = product['price']
            date = product['date']
        
            print(product_id, quantity, price, date)

            # with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                sql = """INSERT INTO carts 
                        (product_id, quantity, price, date) 
                        VALUES (%s, %s, %s, %s)"""
                cursor.execute(sql, (product_id, quantity, price, date))
            connection.commit()

            # with pymysql.connect(**DB_CONFIG) as connection:
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

    finally:
        connection.close()


@app.route('/api/get-history', methods=['GET'])
@login_required
def get_history():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        # with pymysql.connect(**DB_CONFIG) as connection:
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

    finally:
        connection.close()

@app.route('/api/get-filter', methods=['GET'])
@login_required
def get_filter():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        # with pymysql.connect(**DB_CONFIG) as connection:
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

    finally:
        connection.close()

@app.route('/api/get-user', methods=['GET'])
@login_required
def getUser():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        # with pymysql.connect(**DB_CONFIG) as connection:
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
            'pp_url': row[5],
            'status':row[6]} for row in rows]
        # print(result)
        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500

    finally:
        connection.close()

@app.route('/api/add-user', methods=['POST'])
@login_required
def addUser():
    full_name = request.form.get('full_name')
    username = request.form.get('username')
    user_role = request.form.get('role')
    
    password = os.getenv("INITIAL_PASS")
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    print(full_name, username, user_role)

    print(getUser())

    if not all([full_name, username, user_role]):
        return jsonify({"error": "Missing required fields",
                        "message": "Missing required fields"}), 400
    else:
        connection = pymysql.connect(**DB_CONFIG)
        try:    
            # with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                sql = """   INSERT INTO users
                            (full_name, username, password, user_type)
                            VALUES(%s, %s, %s, %s)"""
                cursor.execute(sql, (full_name, username, hashed_password, user_role))
                connection.commit()
                return jsonify({"message": "New User Added successfully"}), 200
        except pymysql.MySQLError as e:
        # Database-specific error handling
            connection.rollback()  # Roll back any partial changes
            return jsonify({
                "error": "Database Error",
                "message": str(e)
            }), 500

        except Exception as e:
            # Catch any other unexpected error
            return jsonify({
                "error": "Server Error",
                "message": str(e)
            }), 500
        finally:
            connection.close()


@app.route('/api/update-user', methods=['POST'])
@login_required
def updateUser():
    user_id = request.form.get('user_id')
    status = request.form.get('status')
    user_role = request.form.get('user_type')

    fields = {}

    if not user_id:
        return jsonify({"success": False, "error": "Missing required field: user_id"}), 400
    else:
        for key, value in request.form.items():
            if value == "" or key == "user_id":
                continue
            else:
                fields.update({key: value})

    if not fields:
        return jsonify({"error": "No valid fields to update"}), 400

    # --------------------------------
    # 3️⃣ Build SQL update statement
    # --------------------------------
    set_clause = ", ".join([f"{key} = %s" for key in fields.keys()])
    values = list(fields.values())
    values.append(user_id)

    query = f"UPDATE users SET {set_clause} WHERE id = %s"

    # --------------------------------
    # 4️⃣ Execute SQL update
    # --------------------------------
    connection = pymysql.connect(**DB_CONFIG)
    try:    
        # with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
            connection.commit()

    finally:
        connection.close()    

    return jsonify({"message": "User Updated successfully"}), 200
@app.route('/api/resetPassword', methods=['POST'])
@login_required
def resetPassword():
    userId = request.form.get('user_id')
    password = os.getenv("INITIAL_PASS")
    hashed_password = hashlib.md5(password.encode()).hexdigest()


    # Check if logged-in user is admin or resetting their own password
    if session['user_type'] not in ('Admin', 'Owner'):
        return jsonify({'error': 'Unauthorized'}), 403

    else:
        connection = pymysql.connect(**DB_CONFIG)
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, userId))
                connection.commit()
                return jsonify({"message": "Password Resetted successfully"}), 200
        except pymysql.MySQLError as e:
        # Database-specific error handling
            connection.rollback()  # Roll back any partial changes
            return jsonify({
                "error": "Database Error",
                "message": str(e)
            }), 500

        except Exception as e:
            # Catch any other unexpected error
            return jsonify({
                "error": "Server Error",
                "message": str(e)
            }), 500
        finally:
            connection.close()

        
       

@app.route('/api/get-report', methods=['GET'])
@login_required
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


    connection = pymysql.connect(**DB_CONFIG)
    try:
        # with pymysql.connect(**DB_CONFIG) as connection:
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

    finally:
        connection.close()

@app.route('/api/get-inventory', methods=['GET'])
@login_required
def get_inventory():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        # with pymysql.connect(**DB_CONFIG) as connection:
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

    finally:
        connection.close()

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
