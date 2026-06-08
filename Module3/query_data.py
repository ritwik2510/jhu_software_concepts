

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "gradcafe",
    "user": "postgres",
    "password": "postgres"
}

def connect():
    return psycopg2.connect(**DB_CONFIG)

def run_query(cur, title, query):
    print("\n" + "="*60)
    print(title)
    print("="*60)

    cur.execute(query)
    result = cur.fetchall()

    for row in result:
        print(row)

def main():
    conn = connect()
    cur = conn.cursor()

    # 1. Fall 2026 count
    run_query(cur,
        "1. Total Fall 2026 applications",
        """
        SELECT COUNT(*) 
        FROM applicants 
        WHERE term ILIKE '%Fall 2026%';
        """
    )

    # 2. % international students
    run_query(cur,
        "2. % International Students",
        """
        SELECT 
        ROUND(
            100.0 * SUM(CASE WHEN us_or_international != 'American' THEN 1 ELSE 0 END)
            / COUNT(*), 2)
        FROM applicants;
        """
    )

    # 3. Average GPA + GRE stats
    run_query(cur,
        "3. Average GPA and GRE scores",
        """
        SELECT
            ROUND(AVG(gpa), 2),
            ROUND(AVG(gre), 2),
            ROUND(AVG(gre_v), 2),
            ROUND(AVG(gre_aw), 2)
        FROM applicants
        WHERE gpa IS NOT NULL;
        """
    )

    # 4. GPA of American students (Fall 2026)
    run_query(cur,
        "4. GPA of American Students (Fall 2026)",
        """
        SELECT ROUND(AVG(gpa), 2)
        FROM applicants
        WHERE term ILIKE '%Fall 2026%'
        AND us_or_international = 'American';
        """
    )

    # 5. % Acceptances
    run_query(cur,
        "5. Percentage of Acceptances (Fall 2026)",
        """
        SELECT ROUND(
            100.0 * SUM(CASE WHEN status ILIKE '%accept%' THEN 1 ELSE 0 END)
            / COUNT(*), 2)
        FROM applicants
        WHERE term ILIKE '%Fall 2026%';
        """
    )

    # 6. GPA of accepted students
    run_query(cur,
        "6. GPA of Accepted Students",
        """
        SELECT ROUND(AVG(gpa), 2)
        FROM applicants
        WHERE status ILIKE '%accept%';
        """
    )

    # 7. JHU MS CS applicants
    run_query(cur,
        "7. JHU MS Computer Science Applicants",
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE program ILIKE '%Johns Hopkins%'
        AND program ILIKE '%Computer Science%'
        AND program ILIKE '%Master%';
        """
    )

    # 8. PhD acceptances at top schools
    run_query(cur,
        "8. PhD Acceptances (MIT, Stanford, CMU, Georgetown)",
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE status ILIKE '%accept%'
        AND term ILIKE '%2026%'
        AND program ILIKE ANY (ARRAY[
            '%MIT%',
            '%Stanford%',
            '%Carnegie Mellon%',
            '%Georgetown%'
        ])
        AND program ILIKE '%PhD%'
        AND program ILIKE '%Computer Science%';
        """
    )

    # 9. Average GPA for each admission status
    run_query(cur,
        "9. Average GPA for each admission status",
        """

        SELECT
            status,
            ROUND(AVG(gpa), 2) AS avg_gpa
        FROM applicants
        WHERE gpa IS NOT NULL
        GROUP BY status
        ORDER BY avg_gpa DESC;
        """
    )

    # 10. Top 10 most applied programs
    run_query(cur,
            "10. Top 10 most applied programs",
            """
            SELECT program, COUNT(*) AS total
            FROM applicants
            GROUP BY program
            ORDER BY total DESC
            LIMIT 10;
            """
    )

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()