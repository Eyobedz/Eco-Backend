from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_session import Session

app = Flask(__name__)

# Secret key for sessions
app.secret_key = "supersecretkey"

# Flask-Session setup
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Sample users dictionary (Replace with database in production)
users = {"admin": {"password": "1234", "role": "admin"}, "user": {"password": "pass", "role": "user"}}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.role = users[username]["role"]

@login_manager.user_loader
def load_user(username):
    if username in users:
        return User(username)
    return None

@app.route("/")
def home():
    return redirect(url_for("login"))  # Redirect to login form immediately

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # Validate user
        if username in users and users[username]["password"] == password:
            user = User(username)
            login_user(user)  # Flask-Login session
            session["role"] = user.role  # Store role in Flask session
            return redirect(url_for("dashboard"))  # Redirect to dashboard.html
        
        return "Invalid credentials! <a href='/login'>Try again</a>"

    return '''<form method="post">
                Username: <input type="text" name="username"><br>
                Password: <input type="password" name="password"><br>
                <input type="submit" value="Login">
              </form>'''

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.id, role=session.get("role"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()  # Clear session
    return redirect(url_for("login"))  # Redirect to login after logout

if __name__ == "__main__":
    app.run(debug=True)
