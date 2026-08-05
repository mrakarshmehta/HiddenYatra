"""
Clean duplicate places in MySQL database hiddenyatra by keeping only the row with the lowest ID for each unique place name.
"""
import pymysql
import os

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'hiddenyatra'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def clean_duplicates():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # Find duplicate names
            cur.execute("""
                SELECT name, MIN(id) as keep_id, COUNT(*) as cnt 
                FROM places 
                WHERE deleted_at IS NULL 
                GROUP BY name 
                HAVING cnt > 1
            """)
            duplicates = cur.fetchall()
            print(f"Found {len(duplicates)} duplicate place groups in database.")

            total_deleted = 0
            for dup in duplicates:
                name = dup['name']
                keep_id = dup['keep_id']
                
                # Delete rows with same name but ID > keep_id
                cur.execute("DELETE FROM places WHERE name = %s AND id > %s", (name, keep_id))
                deleted = cur.rowcount
                total_deleted += deleted
                print(f"  [DEDUPLICATED] '{name}': Kept ID {keep_id}, removed {deleted} duplicate row(s).")

            conn.commit()
            print(f"\nSuccessfully cleaned up {total_deleted} duplicate place rows from MySQL database!")
            
            # Print remaining place count
            cur.execute("SELECT COUNT(*) as cnt FROM places WHERE deleted_at IS NULL")
            res = cur.fetchone()
            print(f"Total unique places in database now: {res['cnt']}")

    finally:
        conn.close()

if __name__ == '__main__':
    clean_duplicates()
