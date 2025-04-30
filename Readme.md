# Flask Portfolio Dashboard

A multi-user portfolio sharing platform built with Flask.  
Users can register, create their own project portfolios and skills, edit their profile (bio, avatar, website link), and interact with others through likes and comments.  
An Admin Dashboard provides full site-wide management capabilities.

---

## 🚀 Features

- 🧑‍💻 User Registration and Login
- 🗂️ Create, Edit, and Delete Portfolio Projects
- 🧠 Add, Edit, and Delete Skills
- 🧑‍🎨 User Profiles with Bio, Avatar, and Website Link
- 🌍 Public Global Stream to showcase all portfolios
- ❤️ Like and 💬 Comment on portfolio projects
- 🛡️ Secure Dashboard for Admins:
  - View all users
  - View all projects
  - View all comments
  - (Future enhancement) Delete inappropriate content
- 📱 Fully responsive UI using Bootstrap 5

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Flask, Flask-Login, SQLAlchemy
- **Frontend:** HTML5, Bootstrap 5, Jinja2 Templating
- **Database:** SQLite (for development)

---

## 🖥️ How to Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/guired513/your-repo-name.git
   cd your-repo-name
  ```
**Set up virtual environment**

    ```bash
    # Set up virtual environment
    python -m venv venv

    # Activate the virtual environment
    source venv/bin/activate   # macOS/Linux
    .\venv\Scripts\activate    # Windows

    # Install dependencies
    pip install -r requirements.txt

    # Run the application
    python app.py
    ```

  Visit in your browser
  http://127.0.0.1:5000/

## 🧪 Important Notes

- On first run, a portfolio.db file is created automatically.
- Register a user and manually promote it to Admin via Flask shell:
    ```bash
    flask shell
    from app import db, User
    user = User.query.filter_by(username='your-admin-username').first()
    user.is_admin = True
    db.session.commit()

## 📸 Screenshots
To be updated later (Landing Page, Dashboard, Admin View, Portfolio Stream)

## 🌐 Live Demo
https://flask-portfolio-dashboard.onrender.com/

## 📋 Future Enhancements

🔥 User-to-User Messaging
🔥 Image upload (instead of URL for avatars)
🔥 Admin content moderation tools
🔥 Full site deployment (PostgreSQL + Gunicorn)

##📄 License

This project is licensed under the MIT License.

## 💬 Acknowledgments

- Flask Documentation
- Bootstrap 5 Framework
- Jinja2 Template Engine
- StackOverflow Community

