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
    # Render homepage
    countries = db_query_all("SELECT slug, name FROM countries ORDER BY name")
    return render_template("index.html", countries=countries)

@app.route("/")
def index():
    return render_template("index.html")

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

#PORTAL
@app.route("/voyager")
def space_page():
    return render_template("space.html")

#HOME BUTTON
@app.route("/backhome")
def backhome_page():
    return render_template("backhome.html")

#FEATURED FRUIT
@app.route("/coconuts")
def coconuts_page():
    return render_template("featuredfruit/coconuts.html")

@app.route("/bananas")
def bananas_page():
    return render_template("featuredfruit/bananas.html")

@app.route("/pineapples")
def pineapples_page():
    return render_template("featuredfruit/pineapples.html")

@app.route("/strawberries")
def strawberries_page():
    return render_template("featuredfruit/strawberries.html")

@app.route("/grapes")
def grapes_page():
    return render_template("featuredfruit/grapes.html")

@app.route("/watermelons")
def watermelons_page():
    return render_template("featuredfruit/watermelons.html")

# GAME
@app.route("/garden")
def gardenTD():
    return render_template("game.html")

if __name__ == "__main__":
    app.run(debug=True)