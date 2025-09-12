from flask import Flask, render_template, url_for, jsonify, abort
import sqlite3
import os
import random

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "fruit.db")

def db_query_one(query, params=()):
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.execute(query, params)
        row = cur.fetchone()
    return row

def db_query_all(query, params=()):
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.execute(query, params)
        rows = cur.fetchall()
    return rows

@app.route("/")
def home():
    # Render your homepage (adapt your existing index.html into this template)
    # You can also pass a small list of featured countries if you want
    countries = db_query_all("SELECT slug, name FROM countries ORDER BY name")
    return render_template("index.html", countries=countries)

@app.route("/random")
def random_page():
    rows = db_query_all("SELECT * FROM countries")
    if not rows:
        abort(404)
    country = random.choice(rows)
    facts = db_query_all(
        "SELECT fruit, fact FROM fruit_facts WHERE country_id = ?",
        (country["id"],)
    )
    return render_template("country.html", country=country, facts=facts)

app.route("/voyager")
def randomizer():
    return render_template("space.html")


if __name__ == "__main__":
    app.run(debug=True)