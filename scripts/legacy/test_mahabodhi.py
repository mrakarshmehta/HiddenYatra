"""Get the exact traceback from Mahabodhi page crash."""
import sys
sys.path.insert(0, '.')
from app import create_app
app = create_app()
app.config['TESTING'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

with app.test_client() as client:
    try:
        r = client.get('/place/mahabodhi-temple-bodh-gaya')
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("SUCCESS! Page loads correctly now.")
        else:
            print(f"Response length: {len(r.data)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
