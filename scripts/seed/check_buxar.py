import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute("SELECT id, name, slug, cover_image, image_url FROM districts WHERE name LIKE '%Buxar%' OR slug='buxar'")
    print("Buxar district record:")
    print(cur.fetchall())

    cur.execute("SELECT id, name, slug, cover_image, image_url FROM districts LIMIT 10")
    print("\nSample 10 districts:")
    for d in cur.fetchall():
        print(d)

conn.close()
