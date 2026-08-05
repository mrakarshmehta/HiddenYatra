import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute("SELECT id, name, category FROM places ORDER BY id")
    places = cur.fetchall()
    print(f"Total places count: {len(places)}")
    for p in places:
        print(f"ID {p['id']}: {p['name']} | Category: {p['category']}")
conn.close()
