import psycopg2
from psycopg2.extras import execute_values


DEST_DB_NAME = "vulnurl"
DEST_DB_USER = "vulnurl"


connection = psycopg2.connect(f"dbname={DEST_DB_NAME} user={DEST_DB_USER}")
connection.autocommit = False 
cursor = connection.cursor()


def add_file_change(file_change_data, urls_data, cwe_data):
    cursor.execute("""
        INSERT INTO file_change (file_change_id, filename, path, code, programming_language)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (file_change_id) DO NOTHING;
    """, file_change_data)

    url_ids = []
    for url in urls_data:
        cursor.execute("""
            INSERT INTO url (full_url, scheme, host, path, query, fragment)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (full_url) DO NOTHING
            RETURNING url_id;
        """, url)
        
        result = cursor.fetchone()
        if result:
            url_ids.append(result[0])
        else:
            cursor.execute("SELECT url_id FROM url WHERE full_url = %s;", (url[0],))
            url_ids.append(cursor.fetchone()[0])

    cursor.execute("""
        INSERT INTO cwe (cwe_id, cwe_name, description, extended_description, url, is_category)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (cwe_id) DO NOTHING
    """, cwe_data)

    file_url_values = []
    for url_id in url_ids:
        file_url_values.append((file_change_data[0], url_id))
    if len(file_url_values) > 0:
        execute_values(cursor, """
            INSERT INTO file_url (file_change_id, url_id)
            VALUES %s
            ON CONFLICT DO NOTHING;
        """, file_url_values)

    cursor.execute("""
        INSERT INTO change_cwe (file_change_id, cwe_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
    """, (file_change_data[0], cwe_data[0]))

    connection.commit()



def close_db():
    connection.close()
