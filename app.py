from flask import Flask, render_template, redirect, request, url_for, session, flash
from functools import wraps
from flask_bcrypt import Bcrypt
import sqlite3
import os

app = Flask(__name__)

# Genererer en sikker, tilfeldig nøkkel i bakgrunnen i stedet for å lagre passordet i klartekst
app.secret_key = os.urandom(24)

bcrypt = Bcrypt(app)

def lag_kommentar_db():
    with sqlite3.connect("kommentar_database.db") as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS kommentarer(
            id INTEGER PRIMARY KEY,
            kommentar TEXT)
            """)
        con.commit()

def lag_reply_db():
    with sqlite3.connect("reply_database.db") as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS replies(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kommentar_id INTEGER,
                    reply TEXT
                    )""")
        con.commit()

def lag_bruker_db():
    with sqlite3.connect("bruker_database.db") as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS brukere(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brukernavn TEXT UNIQUE NOT NULL,
                    passord TEXT NOT NULL,
                    rolle TEXT NOT NULL DEFAULT 'User')
                    """)
        con.commit()

@app.route("/", methods = ["GET", "POST"])
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for('login'))

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        brukernavn = request.form["brukernavn"].strip()
        passord = request.form["passord"]

        if not brukernavn or not passord:
            flash("Alle felt må fylles ut!", "danger")
            return redirect(url_for("register"))

        hashed_passord = bcrypt.generate_password_hash(passord).decode("utf-8")

        try:
            with sqlite3.connect("bruker_database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO brukere (brukernavn, passord, rolle) VALUES (?, ?, ?)",(brukernavn, hashed_passord, "User"))
                con.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Brukernavnet er allerede opptatt.", "danger")
            return redirect(url_for("register"))
    return render_template("register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        brukernavn = request.form["brukernavn"].strip()
        passord = request.form["passord"]

        with sqlite3.connect("bruker_database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT id, passord, rolle FROM brukere WHERE brukernavn = ?",(brukernavn,))
            bruker = cur.fetchone()

        if bruker and bcrypt.check_password_hash(bruker[1], passord):
            session["user_id"] = bruker[0]
            session["brukernavn"] = brukernavn
            session["rolle"] = bruker[2]
            flash("Du er nå logget inn!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Feil brukernavn eller passord.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash("Du må være logget inn.", "warning")
            return redirect(url_for("login"))

        if session.get("rolle") != "Admin":
            flash("Du har ikke tilgang til denne handlingen.", "danger")
            return redirect(url_for("kommenter"))

        return f(*args, **kwargs)

    return decorated_function

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", brukernavn=session["brukernavn"])

@app.route("/kommenter", methods=["GET", "POST"])
def kommenter():
    if "user_id" in session:

        with sqlite3.connect("kommentar_database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM kommentarer")
            kommentar_liste = cur.fetchall()

        with sqlite3.connect("reply_database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM replies")
            svar_liste = cur.fetchall()

        return render_template(
            "hilsen.html",
            kommentar_liste=kommentar_liste,
            svar_liste=svar_liste
        )
    return redirect(url_for('login'))
        
@app.route("/legg_til_kommentar", methods = ["GET", "POST"])
def legg_til_kommentar():
    kommentar = request.form.get("kommentar")
    if kommentar != "":
        with sqlite3.connect("kommentar_database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO kommentarer(kommentar) VALUES(?)",(kommentar,))
            con.commit()
    return redirect("/kommenter")

@app.route("/reply/<id>", methods=["GET", "POST"])
def reply(id):
    with sqlite3.connect("kommentar_database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM kommentarer WHERE id = ?", (id,))
        kommentar = cur.fetchone()

    return render_template("reply.html", kommentar=kommentar)

@app.route("/reply_save/<id>", methods=["POST"])
def reply_save(id):
    reply = request.form.get("reply")

    if reply != "":
        with sqlite3.connect("reply_database.db") as con:
            cur = con.cursor()
            cur.execute(
            "INSERT INTO replies (kommentar_id, reply) VALUES (?, ?)",
            (id, reply)
            )
            con.commit()

    return redirect("/kommenter")

@app.route("/slett_svar/<id>", methods=["POST"])
@admin_required
def slett_svar(id):

    with sqlite3.connect("reply_database.db") as con:
        cur = con.cursor()
        cur.execute(
            "DELETE FROM replies WHERE id = ?",
            (id,)
        )
        con.commit()

    return redirect(url_for("kommenter"))

@app.route("/slett/<id>", methods=["POST"])
@admin_required
def slett(id):

    with sqlite3.connect("kommentar_database.db") as con:
        cur = con.cursor()
        cur.execute(
            "DELETE FROM kommentarer WHERE id = ?",
            (id,)
        )
        con.commit()

    with sqlite3.connect("reply_database.db") as con:
        cur = con.cursor()
        cur.execute(
            "DELETE FROM replies WHERE kommentar_id = ?",
            (id,)
        )
        con.commit()

    return redirect("/kommenter")

@app.route("/rediger/<id>", methods = ["GET", "POST"])
def endre(id):
    with sqlite3.connect("kommentar_database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM kommentarer WHERE id = ?", (id,))
        kommentar = cur.fetchone()
    return render_template("rediger.html", kommentar=kommentar)


@app.route("/oppdater/<id>", methods = ["GET", "POST"])
def oppdater(id):
    kommentar = request.form.get("kommentar")
    if kommentar != "":
        with sqlite3.connect("kommentar_database.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE kommentarer SET kommentar=? WHERE id=?", (kommentar,id))
            con.commit()
    return redirect("/kommenter")

def gjør_til_admin(brukernavn):
    with sqlite3.connect("bruker_database.db") as con:
        cur = con.cursor()
        cur.execute("UPDATE brukere SET rolle = 'Admin' WHERE brukernavn = ?",(brukernavn,))
        con.commit()

if __name__ == "__main__":
    lag_kommentar_db()
    lag_reply_db()
    lag_bruker_db()
    gjør_til_admin("Admin")
    app.run(host='0.0.0.0', port=5500, debug=True)
