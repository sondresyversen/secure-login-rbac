# Secure Login & Role-Based Access Control (RBAC) 🔐

This is a backend web application built with Python and Flask. I made this project to learn more about user authentication, how to hash passwords safely, and how to restrict certain actions based on user roles (Admin vs. User).

### Features
- **User Registration & Login:** Users can create an account and log in.
- **Secure Passwords:** Passwords are never stored in plain text. They are securely hashed using `flask-bcrypt`.
- **Role-Based Access Control (RBAC):** Users get the 'User' role by default. Only users with the 'Admin' role are allowed to delete comments or replies.
- **Route Protection:** I built a custom Python decorator (`@admin_required`) that works like a doorman to protect admin-only routes.
- **Databases:** The app automatically creates and manages three separate SQLite3 databases for users, comments, and replies.

### How the Admin Check Works
Instead of writing the same permission check inside every single route, I created this decorator to handle security automatically:

```python
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("rolle") != "Admin":
            return redirect(url_for("kommenter"))
        return f(*args, **kwargs)
    return decorated_function
```

### Technologies Used
- **Backend:** Python & Flask
- **Security:** Flask-Bcrypt (for password hashing)
- **Database:** SQLite3
- **Frontend:** HTML & Jinja2 templates

### 🚀 Future Improvements & Scalability

If I were to scale this application further or prepare it for a production environment, I would:
* **Implement Environment Variables:** Move database names and secret keys out of `app.py` and into a `.env` file to separate settings from the source code.
* **Centralize the Database:** Switch from three separate SQLite instances to a single relational database (like PostgreSQL) with multi-table relations to follow proper database normalization.
* **Add automated testing:** Write Unit Tests for the `@admin_required` decorator to automatically verify that unauthorized users are always blocked.

### How to Run Locally
1. Clone this repository to your machine:
   ```bash
   git clone https://github.com/sondresyversen/secure-login-rbac/
   ```
2. Install the required Python packages:
   ```bash
   pip install Flask flask-bcrypt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open your browser and go to: `http://localhost:5500`


