CREATE TABLE file_change (
    file_change_id TEXT PRIMARY KEY,
    filename TEXT,
    path TEXT,
    code TEXT,
    programming_language TEXT
);

CREATE TABLE url (
    url_id SERIAL PRIMARY KEY,
    full_url TEXT UNIQUE,
    scheme TEXT,
    host TEXT,
    path TEXT,
    query TEXT,
    fragment TEXT
);

CREATE TABLE file_url (
    file_change_id TEXT,
    url_id INTEGER,
    PRIMARY KEY (file_change_id, url_id),
    FOREIGN KEY (file_change_id) REFERENCES file_change(file_change_id) ON DELETE CASCADE,
    FOREIGN KEY (url_id) REFERENCES url(url_id) ON DELETE CASCADE
);

CREATE TABLE cwe (
    cwe_id TEXT PRIMARY KEY,
    cwe_name TEXT,
    description TEXT,
    extended_description TEXT,
    url TEXT,
    is_category BOOLEAN
);

CREATE TABLE change_cwe (
    file_change_id TEXT,
    cwe_id TEXT,
    PRIMARY KEY (file_change_id, cwe_id),
    FOREIGN KEY (file_change_id) REFERENCES file_change(file_change_id) ON DELETE CASCADE,
    FOREIGN KEY (cwe_id) REFERENCES cwe(cwe_id) ON DELETE CASCADE
);


GRANT USAGE ON SCHEMA public TO vulnurl;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vulnurl;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vulnurl;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO vulnurl;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO vulnurl;
