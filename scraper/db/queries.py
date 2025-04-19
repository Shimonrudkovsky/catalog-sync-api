CREATE_TABLES_QUERY = """
CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    time_start TIMESTAMP NOT NULL,
    time_end TIMESTAMP
);

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
    scan_id INT NOT NULL,
    UNIQUE (maker_id, category_id, model_id, part_number, part_category, url, scan_id),
    FOREIGN KEY (maker_id) REFERENCES makers (id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models (id) ON DELETE CASCADE,
    FOREIGN KEY (scan_id) REFERENCES scans (id) ON DELETE CASCADE
);
"""

GET_NEW_SCAN_ID = """
INSERT INTO scans (time_start)
VALUES ($1)
RETURNING scans.id
"""

SCAN_ENDED = """
UPDATE scans
SET time_end = ($2)
WHERE id = ($1)
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
INSERT INTO parts (maker_id, category_id, model_id, part_number, part_category, url, scan_id)
VALUES (
    COALESCE((SELECT id FROM maker_insert), (SELECT id FROM makers WHERE maker = $1)),
    COALESCE((SELECT id FROM category_insert), (SELECT id FROM categories WHERE category = $2)),
    COALESCE((SELECT id FROM model_insert), (SELECT id FROM models WHERE model = $3)),
    $4, $5, $6, $7
);
"""
