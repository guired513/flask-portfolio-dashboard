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

# Models
#--------------------------------------------------------------------------

from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Add these methods:
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Make sure you still have these new profile fields:
    bio = db.Column(db.Text, default="")
    avatar_url = db.Column(db.String(300), default="")
    website_url = db.Column(db.String(300), default="")

    # And relationships if added:
    projects = db.relationship('Project', backref='user', lazy=True)
    skills = db.relationship('Skill', backref='user', lazy=True)

    display_name = db.Column(db.String(100), default="")
    is_admin = db.Column(db.Boolean, default=False)

# Create the database model for Project
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Like', backref='project', lazy=True)
    comments = db.relationship('Comment', backref='project', lazy=True)

# Create the database model for Skill
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user = db.relationship('User', backref='comments', lazy=True)


# Create the database file and tables
with app.app_context():
    db.create_all()



# Setup Flask-Login
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# Mock User Database (Only you)


# Fake User (Admin only)
"""users = {
    "admin": User(id=1, username="admin", password="adminpass")  # You can change the password later
}"""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# Routes
#---------------------------------------------------------------------
@app.route("/")
def home():
    return redirect(url_for("stream_view"))

"""@app.route("/")
def home():
    projects = Project.query.all()
    skills = Skill.query.all()
    return render_template("public_portfolio.html", projects=projects, skills=skills)
"""
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("stream_view"))
        else:
            flash("Invalid credentials.")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)

@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.display_name = request.form.get("display_name")
        current_user.bio = request.form.get("bio")
        current_user.avatar_url = request.form.get("avatar_url")
        current_user.website_url = request.form.get("website_url")
        db.session.commit()
        flash("Profile updated!")
        return redirect(url_for("my_portfolio"))
    return render_template("edit_profile.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(username=username).first():
            flash("Username already taken.")
            return redirect(url_for("register"))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please login.")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/admin")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Access denied. Admins only.")
        return redirect(url_for('stream_view'))

    users = User.query.all()
    projects = Project.query.all()
    comments = Comment.query.all()
    return render_template("admin_dashboard.html", users=users, projects=projects, comments=comments)


@app.route("/stream")
@login_required
def stream_view():
    projects = Project.query.all()
    skills = Skill.query.all()
    return render_template("stream.html", projects=projects, skills=skills)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/my-portfolio")
@login_required
def my_portfolio():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    return render_template("my_portfolio.html", projects=projects, skills=skills)

# Admin: List all projects
@app.route("/projects")
@login_required
def list_projects():
    projects = Project.query.filter_by(user_id=current_user.id).all()
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
        new_project = Project(title=title, description=description, link=link, image_url=image_url, user_id=current_user.id)
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for("list_projects"))
    return render_template("projects/create_project.html")

# Admin: Edit a project
@app.route("/projects/edit/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash("Unauthorized access.")
        return redirect(url_for("list_projects"))
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
    if project.user_id != current_user.id:
        flash("Unauthorized access.")
        return redirect(url_for("list_projects"))
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for("list_projects"))

@app.route("/portfolio")
def public_portfolio():
    projects = Project.query.all()
    return render_template("public_portfolio.html", projects=projects)

# Admin: List all skills
@app.route("/skills")
@login_required
def list_skills():
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    return render_template("skills/list_skills.html", skills=skills)

# Admin: Create new skill
@app.route("/skills/create", methods=["GET", "POST"])
@login_required
def create_skill():
    if request.method == "POST":
        name = request.form.get("name")
        level = request.form.get("level")
        new_skill = Skill(name=name, level=level, user_id=current_user.id)
        db.session.add(new_skill)
        db.session.commit()
        return redirect(url_for("list_skills"))
    return render_template("skills/create_skill.html")

# Admin: Edit a skill
@app.route("/skills/edit/<int:skill_id>", methods=["GET", "POST"])
@login_required
def edit_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if project.user_id != skill_user.id:
        flash("Unauthorized access.")
        return redirect(url_for("list_projects"))
    if request.method == "POST":
        skill.name = request.form.get("name")
        skill.level = request.form.get("level")
        db.session.commit()
        return redirect(url_for("list_skills"))
    return render_template("skills/edit_skill.html", skill=skill)

# Admin: Delete a skill
@app.route("/skills/delete/<int:skill_id>")
@login_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if project.user_id != skill_user.id:
        flash("Unauthorized access.")
        return redirect(url_for("list_projects"))
    db.session.delete(skill)
    db.session.commit()
    return redirect(url_for("list_skills"))

#like/unlike route
@app.route("/project/<int:project_id>/like", methods=["POST"])
@login_required
def like_project(project_id):
    project = Project.query.get_or_404(project_id)

    if project.user_id == current_user.id:
        flash("You can't like your own project.")
        return redirect(url_for('stream_view'))

    like = Like.query.filter_by(user_id=current_user.id, project_id=project_id).first()
    if like:
        db.session.delete(like)
    else:
        db.session.add(Like(user_id=current_user.id, project_id=project_id))
    db.session.commit()
    return redirect(url_for('stream_view'))


#comment route
@app.route("/project/<int:project_id>/comment", methods=["POST"])
@login_required
def comment_project(project_id):
    content = request.form.get("content")
    if content:
        new_comment = Comment(content=content, user_id=current_user.id, project_id=project_id)
        db.session.add(new_comment)
        db.session.commit()
    return redirect(url_for('stream_view'))

if __name__ == "__main__":
    app.run(debug=True)