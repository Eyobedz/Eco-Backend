from flask import Flask, jsonify, request, send_from_directory
import pymysql
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/get-data', methods=['GET'])
def get_data():
    try:
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name, age, image_url FROM students")
                rows = cursor.fetchall()

        result = [{'name': row[0],
                   'age': row[1],
                   'image_url': row[2]} for row in rows]
        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500



@app.route('/api/add-student', methods=['POST'])
def add_student():
    if 'image' not in request.files:
        return jsonify({"error": "No image file"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        name = request.form.get('name')
        age = request.form.get('age')
        image_url = f"/uploads/{filename}"
        
        try:
            with pymysql.connect(**DB_CONFIG) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO students (name, age, image_url) VALUES (%s, %s, %s)", 
                                   (name, age, image_url))
                connection.commit()
            return jsonify({"message": "Student added successfully"}), 201
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "An error occurred while adding the student"}), 500
    
    return jsonify({"error": "Invalid file type"}), 400



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/api/update-student', methods=['PUT'])
def update_student():
    if 'image' not in request.files:
        # Handle update without image
        data = request.form
        try:
            with pymysql.connect(**DB_CONFIG) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE students SET age = %s WHERE name = %s", (data['age'], data['name']))
                connection.commit()
            return jsonify({"message": "Student updated successfully"}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "An error occurred while updating the student"}), 500
    
    # Handle update with image
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        name = request.form.get('name')
        age = request.form.get('age')
        image_url = f"/uploads/{filename}"
        
        try:
            with pymysql.connect(**DB_CONFIG) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE students SET age = %s, image_url = %s WHERE name = %s", 
                                   (age, image_url, name))
                connection.commit()
            return jsonify({"message": "Student updated successfully"}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "An error occurred while updating the student"}), 500
    
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/api/delete-student', methods=['DELETE'])
def delete_student():
    data = request.json
    try:
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM students WHERE name = %s", (data['name'],))
            connection.commit()
        return jsonify({"message": "Student deleted successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while deleting the student"}), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
