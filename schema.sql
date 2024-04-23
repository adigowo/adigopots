-- schema.sql
CREATE TABLE potions (
    potion_id SERIAL PRIMARY KEY,
    potion_name VARCHAR(255) NOT NULL,
    red INT NOT NULL,
    green INT NOT NULL,
    blue INT NOT NULL,
    dark INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    inventory INT NOT NULL
);

