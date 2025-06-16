import psycopg2
import url_extracting
import db_update


SRC_DB_NAME = "postgrescvedumper"
SRC_DB_USER = "postgrescvedumper"


def main():
    """Main function connects to database, then in a loop it gets batches processes them"""

    # Connect to database 'postgrescvedumper'
    connection = psycopg2.connect(f"dbname={SRC_DB_NAME} user={SRC_DB_USER}")
    cursor = connection.cursor()

    # Get the file changes in batches
    cursor.execute("""
                    DECLARE batch_cursor CURSOR FOR 
                    SELECT 
                        file_change.file_change_id,
                        file_change.filename,
                        file_change.old_path,
                        file_change.code_before,
                        file_change.programming_language,
                        cwe.cwe_id,
                        cwe.cwe_name,
                        cwe.description,
                        cwe.extended_description,
                        cwe.url,
                        cwe.is_category
                    FROM 
                        file_change
                    JOIN 
                        fixes ON file_change.hash = fixes.hash
                    JOIN 
                        cwe_classification ON fixes.cve_id = cwe_classification.cve_id
                    JOIN 
                        cwe ON cwe_classification.cwe_id = cwe.cwe_id;
                    """)

    batch_size = 500
    rows_processed = 0
    while True:
        cursor.execute(f"FETCH {batch_size} FROM batch_cursor;")
        rows = cursor.fetchall()

        # Stop if there are no more rows
        if not rows:
            break

        process_batch(rows)
        rows_processed += batch_size
        print(f"Rows processed: {rows_processed}")


    cursor.execute("CLOSE batch_cursor;")
    cursor.close()
    connection.close()
    db_update.close_db()



checked_files = {}
def process_batch(rows):
    """Called for every batch. Extracts the URLs from comments and puts the data in the database"""
    for row in rows:
        file_change_data = row[:5]
        urls_data = []
        cwe_data = row[5:]

        # If URLs already extracted from file, only add new CWE to database
        if row[0] in checked_files:
            if checked_files[row[0]]:
                db_update.add_file_change(file_change_data, urls_data, cwe_data)
            else:
                continue


        # First time seeing file, get URLs and add to database
        else:
            code = row[3]
            programming_language = row[4]
            try:
                urls_data = url_extracting.extract_comment_urls(code, programming_language)
                if len(urls_data) > 0:
                    checked_files[row[0]] = True
                    db_update.add_file_change(file_change_data, urls_data, cwe_data)
            except ValueError:
                checked_files[row[0]] = False
                



if __name__ == "__main__":
    main()
