CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    exercise_name VARCHAR(100) NOT NULL,
    weight DECIMAL(5, 2) NOT NULL,
    repetitions INT NOT NULL,
    sets INT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);