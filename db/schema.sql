DROP TABLE IF EXISTS countries;
DROP TABLE IF EXISTS fruit_facts;

CREATE TABLE countries (
  id INTEGER PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  summary TEXT,
  hero_image TEXT
);

CREATE TABLE fruit_facts (
  id INTEGER PRIMARY KEY,
  country_id INTEGER NOT NULL REFERENCES countries(id),
  fruit TEXT NOT NULL,
  fact TEXT NOT NULL
);
