import re
import psycopg2


SRC_DB_NAME = "vulnurl"
SRC_DB_USER = "vulnurl"

DEST_DB_NAME = "vulnurl_filtered"
DEST_DB_USER = "vulnurl"



ALLOWED_HOSTNAMES = {
    'github.com', 'gitlab.com', 'bitbucket.org', 'gist.github.com',
    'stackoverflow.com', 'reddit.com', 'dev.to',
    'pastebin.com', 'hastebin.com'
}

ALLOWED_PATH_PATTERNS = [
    re.compile(r'.*\.(py|js|java|cpp)$'),
    re.compile(r'.*/src/.*'),
    re.compile(r'.*/examples?/.*'),
    re.compile(r'.*/blob/.*')
]

BLOCKED_PATH_PATTERNS = [
    re.compile(r'.*/LICENSE.*'),
    re.compile(r'.*/README.*'),
    re.compile(r'.*/docs?/.*'),
    re.compile(r'.*/issues/.*'),
    re.compile(r'.*/blog/.*')
]


def is_url_allowed(host, path):
    if any(p.match(path) for p in BLOCKED_PATH_PATTERNS):
        return False
    if host in ALLOWED_HOSTNAMES or any(p.match(path) for p in ALLOWED_PATH_PATTERNS):
        return True
    return False


def main():
    source_conn = psycopg2.connect(f"dbname={SRC_DB_NAME} user={SRC_DB_USER}")
    dest_conn = psycopg2.connect(f"dbname={DEST_DB_NAME} user={DEST_DB_USER}")

    with source_conn, dest_conn:
        with source_conn.cursor() as src, dest_conn.cursor() as dst:
            # Fetch URLs and filter them
            src.execute("SELECT * FROM url")
            urls = src.fetchall()
            filtered_url_ids = {}
            for url in urls:
                url_id, full_url, scheme, host, path, query, fragment = url
                if is_url_allowed(host, path):
                    dst.execute("""
                        INSERT INTO url (url_id, full_url, scheme, host, path, query, fragment)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (url_id, full_url, scheme, host, path, query, fragment))
                    filtered_url_ids[url_id] = True

            # Copy file_change entries that are linked to at least one valid URL
            src.execute("SELECT DISTINCT fc.* FROM file_change fc "
                        "JOIN file_url fu ON fc.file_change_id = fu.file_change_id "
                        "WHERE fu.url_id = ANY(%s)", (list(filtered_url_ids.keys()),))
            file_changes = src.fetchall()
            for fc in file_changes:
                dst.execute("""
                    INSERT INTO file_change (file_change_id, filename, path, code, programming_language)
                    VALUES (%s, %s, %s, %s, %s)
                """, fc)

            # Copy file_url for valid URLs and their associated file changes
            src.execute("SELECT * FROM file_url WHERE url_id = ANY(%s)", (list(filtered_url_ids.keys()),))
            for file_change_id, url_id in src.fetchall():
                dst.execute("INSERT INTO file_url (file_change_id, url_id) VALUES (%s, %s)",
                            (file_change_id, url_id))

            # Copy CWE and change_cwe for included file changes
            src.execute("SELECT DISTINCT c.* FROM cwe c JOIN change_cwe cc ON c.cwe_id = cc.cwe_id "
                        "WHERE cc.file_change_id IN (SELECT file_change_id FROM file_change)")
            for row in src.fetchall():
                dst.execute("""
                    INSERT INTO cwe (cwe_id, cwe_name, description, extended_description, url, is_category)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, row)

            # Fetch file_change_ids that were actually inserted into the destination
            dst.execute("SELECT file_change_id FROM file_change")
            valid_file_change_ids = {row[0] for row in dst.fetchall()}

            # Now filter and insert only those change_cwe rows whose file_change_id is in the set
            src.execute("SELECT * FROM change_cwe")
            for file_change_id, cwe_id in src.fetchall():
                if file_change_id in valid_file_change_ids:
                    dst.execute("INSERT INTO change_cwe (file_change_id, cwe_id) VALUES (%s, %s)",
                                (file_change_id, cwe_id))

    print("Filtering and copying complete.")

if __name__ == "__main__":
    main()
