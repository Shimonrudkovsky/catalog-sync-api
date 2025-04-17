CREATE_TABLES_QUERY = """
CREATE TABLE IF NOT EXISTS makers (
    id SERIAL PRIMARY KEY,
    maker TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    model TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS parts (
    id SERIAL PRIMARY KEY,
    maker_id INT NOT NULL,
    category_id INT NOT NULL,
    model_id INT NOT NULL,
    part_number TEXT NOT NULL,
    part_category TEXT NOT NULL,
    url TEXT NOT NULL,
    UNIQUE (maker_id, category_id, model_id, part_number, part_category),
    FOREIGN KEY (maker_id) REFERENCES makers (id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models (id) ON DELETE CASCADE
);
"""

INSERT_DATA_QUERY = """
WITH maker_insert AS (
    INSERT INTO makers (maker)
    VALUES ($1)
    ON CONFLICT (maker) DO NOTHING
    RETURNING id
),
category_insert AS (
    INSERT INTO categories (category)
    VALUES ($2)
    ON CONFLICT (category) DO NOTHING
    RETURNING id
),
model_insert AS (
    INSERT INTO models (model)
    VALUES ($3)
    ON CONFLICT (model) DO NOTHING
    RETURNING id
)
INSERT INTO parts (maker_id, category_id, model_id, part_number, part_category, url)
VALUES (
    COALESCE((SELECT id FROM maker_insert), (SELECT id FROM makers WHERE maker = $1)),
    COALESCE((SELECT id FROM category_insert), (SELECT id FROM categories WHERE category = $2)),
    COALESCE((SELECT id FROM model_insert), (SELECT id FROM models WHERE model = $3)),
    $4, $5, $6
);
"""
