from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'  # Replace this in production!

# After setting up app and login manager
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create the database model for Project
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(200), nullable=True)

# Create the database file and tables
with app.app_context():
    db.create_all()



# Setup Flask-Login
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# Mock User Database (Only you)
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Fake User (Admin only)
users = {
    "admin": User(id=1, username="admin", password="adminpass")  # You can change the password later
}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

# Routes
@app.route("/")
def home():
    return "Welcome to My Portfolio Dashboard! <a href='/login'>Login</a>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = users.get(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Please try again.")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# Admin: List all projects
@app.route("/projects")
@login_required
def list_projects():
    projects = Project.query.all()
    return render_template("projects/list_projects.html", projects=projects)

# Admin: Create new project
@app.route("/projects/create", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        link = request.form.get("link")
        image_url = request.form.get("image_url")
        new_project = Project(title=title, description=description, link=link, image_url=image_url)
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for("list_projects"))
    return render_template("projects/create_project.html")

# Admin: Edit a project
@app.route("/projects/edit/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == "POST":
        project.title = request.form.get("title")
        project.description = request.form.get("description")
        project.link = request.form.get("link")
        project.image_url = request.form.get("image_url")
        db.session.commit()
        return redirect(url_for("list_projects"))
    return render_template("projects/edit_project.html", project=project)

# Admin: Delete a project
@app.route("/projects/delete/<int:project_id>")
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for("list_projects"))


if __name__ == "__main__":
    app.run(debug=True)