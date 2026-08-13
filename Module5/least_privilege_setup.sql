CREATE ROLE gradcafe_app WITH LOGIN PASSWORD 'gradcafe_app_pw123';

GRANT CONNECT ON DATABASE gradcafe TO gradcafe_app;

GRANT SELECT, INSERT, UPDATE ON applicants TO gradcafe_app;
GRANT USAGE, SELECT ON SEQUENCE applicants_p_id_seq TO gradcafe_app;
