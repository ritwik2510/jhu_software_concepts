CREATE TABLE IF NOT EXISTS applicants (
    p_id SERIAL PRIMARY KEY,
    degree TEXT,
    program TEXT,
    comments TEXT,
    date_added TEXT,
    url TEXT UNIQUE,
    status TEXT,
    term TEXT,
    us_or_international TEXT,
    gpa REAL,
    gre REAL,
    gre_v REAL,
    gre_aw REAL,
    llm_generated_program TEXT,
    llm_generated_university TEXT
);