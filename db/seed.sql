INSERT INTO countries (slug, name, summary, hero_image) VALUES
  ('japan','Japan','Home to unique fruits like yuzu and persimmon.','/static/images/countries/japan.jpg'),
  ('brazil','Brazil','Huge variety of tropical fruits across biomes.','/static/images/countries/brazil.jpg'),
  ('greece','Greece','Mediterranean climate with figs and citrus.','/static/images/countries/greece.jpg');

INSERT INTO fruit_facts (country_id, fruit, fact)
SELECT id,'Persimmon','Persimmons (kaki) are common in autumn markets.' FROM countries WHERE slug='japan';
INSERT INTO fruit_facts (country_id, fruit, fact)
SELECT id,'Yuzu','Aromatic citrus used in sauces and baths.' FROM countries WHERE slug='japan';

INSERT INTO fruit_facts (country_id, fruit, fact)
SELECT id,'Açaí','Often served as a frozen pulp or smoothie.' FROM countries WHERE slug='brazil';
INSERT INTO fruit_facts (country_id, fruit, fact)
SELECT id,'Cupuaçu','Chocolatey-aroma fruit from the Amazon.' FROM countries WHERE slug='brazil';

INSERT INTO fruit_facts (country_id, fruit, fact)
SELECT id,'Fig','Fresh and dried figs are staples.' FROM countries WHERE slug='greece';
INSERT INTO fruit_facts (country_id, fruit, fact)
SELECT id,'Citrus','Oranges and lemons thrive in the climate.' FROM countries WHERE slug='greece';
