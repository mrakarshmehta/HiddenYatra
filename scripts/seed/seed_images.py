"""
Add cover images (Unsplash URLs) to all places.
Run: python seed_images.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import init_db, get_db

def seed_images():
    init_db()
    conn = get_db()

    # Map place names to Unsplash image URLs
    images = {
        # Bihar
        "Mahabodhi Temple, Bodh Gaya": "https://images.unsplash.com/photo-1591018653367-4e4f0b5e2be1?w=900&q=80",
        "Nalanda University Ruins": "https://images.unsplash.com/photo-1624461681464-844e56e09c28?w=900&q=80",
        "Patna Sahib Gurudwara (Takht Sri Patna Sahib)": "https://images.unsplash.com/photo-1609947017136-9daf32a15c28?w=900&q=80",
        "Rajgir (Rajagriha)": "https://images.unsplash.com/photo-1506461883276-594a12b11cf3?w=900&q=80",
        "Vaishali - Birthplace of Democracy": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=900&q=80",
        "Vikramshila University Ruins": "https://images.unsplash.com/photo-1590050752117-238cb78a0b65?w=900&q=80",
        "Madhubani - Art Village": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=900&q=80",
        "Sher Shah Suri Tomb, Sasaram": "https://images.unsplash.com/photo-1585136917228-c5a65eb8a40e?w=900&q=80",
        "Golghar, Patna": "https://images.unsplash.com/photo-1600100397608-e18b4a498a73?w=900&q=80",
        "Mundeshwari Temple": "https://images.unsplash.com/photo-1609948543911-7060908bd428?w=900&q=80",
        # Rajasthan
        "Hawa Mahal": "https://images.unsplash.com/photo-1599661046289-e31897846e41?w=900&q=80",
        "Mehrangarh Fort": "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=900&q=80",
        "City Palace, Udaipur": "https://images.unsplash.com/photo-1568495248636-6432b97bd949?w=900&q=80",
        # Uttar Pradesh
        "Taj Mahal": "https://images.unsplash.com/photo-1564507592924-0bb5a26b4547?w=900&q=80",
        "Varanasi Ghats": "https://images.unsplash.com/photo-1561361513-2d000a50f0dc?w=900&q=80",
        # Kerala
        "Backwaters of Alleppey": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=900&q=80",
        "Munnar Tea Gardens": "https://images.unsplash.com/photo-1595815771614-ade9d652a65d?w=900&q=80",
        # Maharashtra
        "Gateway of India": "https://images.unsplash.com/photo-1567157577867-05ccb1388e13?w=900&q=80",
        # Goa
        "Calangute Beach": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=900&q=80",
        # Tamil Nadu
        "Meenakshi Amman Temple": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=900&q=80",
        # Karnataka
        "Hampi": "https://images.unsplash.com/photo-1590050752117-238cb78a0b65?w=900&q=80",
        # Himachal Pradesh
        "Shimla Ridge": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=900&q=80",
        "Manali - Solang Valley": "https://images.unsplash.com/photo-1585136917228-c5a65eb8a40e?w=900&q=80",
        # West Bengal
        "Victoria Memorial": "https://images.unsplash.com/photo-1558431382-27e303142255?w=900&q=80",
        # J&K
        "Dal Lake": "https://images.unsplash.com/photo-1597074866923-dc0589150458?w=900&q=80",
        # Uttarakhand
        "Rishikesh": "https://images.unsplash.com/photo-1585136917228-c5a65eb8a40e?w=900&q=80",
        # Gujarat
        "Rann of Kutch": "https://images.unsplash.com/photo-1609947017136-9daf32a15c28?w=900&q=80",
    }

    updated = 0
    for name, url in images.items():
        result = conn.execute("UPDATE places SET cover_image = ? WHERE name = ?", (url, name))
        if result.rowcount > 0:
            updated += 1
            print(f"  + {name}")
        else:
            print(f"  ! Not found: {name}")

    conn.commit()
    conn.close()
    print(f"\nDone! Updated {updated} place cover images.")


if __name__ == "__main__":
    seed_images()
