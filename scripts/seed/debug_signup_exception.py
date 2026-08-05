"""Run Flask test_client to capture the exact exception during signup POST."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.stdout.reconfigure(encoding='utf-8')

import pymysql
from app import create_app

# Clean DB first
conn = pymysql.connect(host='localhost', user='root', database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute("DELETE FROM users WHERE username='tb_user_999'")
conn.commit()
conn.close()

app = create_app()
app.testing = True  # Propagate exceptions

client = app.test_client()
with client:
    res = client.get('/signup')
    import re
    token = re.search(r'name="_csrf_token" value="([^"]+)"', res.text).group(1)
    
    data = {
        '_csrf_token': token,
        'full_name': 'Traceback Test',
        'username': 'tb_user_999',
        'email': 'tb_user_999@example.com',
        'password': 'Password123',
        'confirm_password': 'Password123'
    }
    
    print("Sending POST request...")
    try:
        res2 = client.post('/signup', data=data)
        print("Status:", res2.status_code)
        print("Location:", res2.headers.get('Location'))
    except Exception as e:
        import traceback
        print("EXACT EXCEPTION TRACEBACK:")
        traceback.print_exc()
