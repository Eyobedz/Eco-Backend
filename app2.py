from flask import Flask, render_template, Response
from flask_mysqldb import MySQL
import time
import json

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Eyobed579@papa'
app.config['MYSQL_DB'] = 'organicdb'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students')
def students():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    cur.close()
    return {'students': data}

def generate_updates():
    """Generator to yield updates whenever there are changes in the database."""
    last_id = 0
    while True:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students")
        data = cur.fetchall()
        cur.close()

        # Check if data has changed
        if data and data[0][0] != last_id:
            last_id = data[0][0]  # Assuming ID is always increasing
            yield f"data: {json.dumps(data)}\n\n"

        time.sleep(5)  # Check for updates every 5 seconds

@app.route('/updates')
def updates():
    return Response(generate_updates(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
