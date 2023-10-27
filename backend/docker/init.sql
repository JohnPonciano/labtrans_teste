-- Cria a tabela "Highway"
CREATE TABLE IF NOT EXISTS "highway" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(255),
    "highway" INT,
    "UF" VARCHAR(255),
    "item" VARCHAR(255),
    "latitude" VARCHAR(255),
    "longitude" VARCHAR(255),
    "exp_km_calc" FLOAT
);

-- Cria a tabela "Results"
CREATE TABLE IF NOT EXISTS "results" (
    "id" SERIAL PRIMARY KEY,
    "highway" INT UNIQUE,
    "buraco" INT,
    "remendo" INT,
    "trinca" INT,
    "placa" INT,
    "drenagem" INT,
    "created_at" TIMESTAMPTZ
);
