CREATE TABLE IF NOT EXISTS applicants (
    id SERIAL PRIMARY KEY,
    program TEXT,
    comments TEXT,
    date_added TEXT,
    url TEXT,
    status TEXT,
    term TEXT,
    us_or_international TEXT,
    gpa FLOAT,
    gre INT,
    gre_v INT,
    gre_aw FLOAT,
    llm_generated_program TEXT,
    llm_generated_university TEXT
);