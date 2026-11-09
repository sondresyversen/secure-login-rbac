# Secure Login & Role-Based Access Control (RBAC) 🔐

A secure backend web application built with Python and the Flask framework. The project implements a robust authentication layer utilizing password hashing via Bcrypt, relational data storage with SQLite3, and custom route decorators to enforce Role-Based Access Control (RBAC).

### Key Features
- **Secure Authentication:** Implements industry-standard password hashing using `flask-bcrypt` to prevent plain-text storage of credentials.
- **Role-Based Access Control (RBAC):** Restricts dangerous endpoints (such as deleting content) to authorized accounts using a custom `@admin_required` python decorator.
- **Relational Databases:** Utilizes multiple isolated SQLite3 database tables to manage users, comments, and replies dynamically.
- **Session Management:** Handles secure state retention across user interactions using cryptographic cookies (`app.secret_key`).

### Identity & Access Logic
The system automatically spins up the environment and seed records on initialization. Dangerous actions leverage a structural decorator architecture:

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

### Built With
- **Backend Framework:** Python & Flask
- **Security & Hashing:** Flask-Bcrypt
- **Database Engine:** SQLite3
- **Frontend Layer:** Jinja2 Templating HTML Engine

### How to Run Locally
1. Clone the repository:
   ```bash
   git clone https://github.com
   ```
2. Install the required backend dependencies:
   ```bash
   pip install Flask flask-bcrypt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Access the local web node at: `http://localhost:5500`

