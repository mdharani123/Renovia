"""
Seed script to populate PostgreSQL with realistic test data for SIH 2026.
Creates 10 collectors, 5 recyclers (verified & unverified), 20 scrap items, 15 offers, 10 transactions.
"""
import sys
import os
import random
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.database import SessionLocal, engine, Base
from app.models.models import User, Collector, Recycler, ScrapItem, Offer, Transaction, RecyclingRecord, UserRole, ScrapStatus, OfferStatus, PickupStatus, RecyclingStatus
from app.auth.security import get_password_hash

def seed_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("Seeding Users, Collectors, and Recyclers...")
    
    # 1. Admin User
    admin_user = User(
        name="SIH Admin",
        phone="9000000000",
        email="admin@kabadiwala.org",
        password_hash=get_password_hash("Admin@123"),
        role=UserRole.ADMIN,
        location="Chennai, TN"
    )
    db.add(admin_user)

    # 2. 10 Collectors
    collectors = []
    for i in range(1, 11):
        u = User(
            name=f"Collector {i}",
            phone=f"987654321{i-1}",
            email=f"collector{i}@gmail.com",
            password_hash=get_password_hash("Collector@123"),
            role=UserRole.COLLECTOR,
            location=f"Zone {i}, Chennai"
        )
        db.add(u)
        db.flush()
        
        c = Collector(
            user_id=u.id,
            address=f"Street {i}, Block {chr(64+i)}, Chennai",
            latitude=13.0827 + (i * 0.005),
            longitude=80.2707 + (i * 0.005),
            verification_status=True
        )
        db.add(c)
        collectors.append(c)

    # 3. 5 Recyclers
    recycler_configs = [
        ("GreenTech Eco Recyclers", "LIC-TN-2026-001", ["E-waste", "Metal"], 13.0850, 80.2750, True, 4.8),
        ("Apex Paper & Plastic Solutions", "LIC-TN-2026-002", ["Paper", "Plastic"], 13.0900, 80.2800, True, 4.5),
        ("Metals India Ltd", "LIC-TN-2026-003", ["Metal", "E-waste", "Glass"], 13.0700, 80.2500, True, 4.9),
        ("Universal Scrap Processing", "LIC-TN-2026-004", ["Plastic", "Glass", "Mixed waste"], 13.0600, 80.2400, False, 3.8),
        ("CleanEarth E-Cycle", "LIC-TN-2026-005", ["E-waste", "Metal", "Plastic"], 13.1000, 80.2900, True, 4.7)
    ]

    recyclers = []
    for idx, (comp, lic, mats, lat, lon, verif, rat) in enumerate(recycler_configs, start=1):
        u = User(
            name=f"{comp} Admin",
            phone=f"912345678{idx-1}",
            email=f"contact@recycler{idx}.com",
            password_hash=get_password_hash("Recycler@123"),
            role=UserRole.RECYCLER,
            location="Chennai Industrial Belt"
        )
        db.add(u)
        db.flush()

        r = Recycler(
            user_id=u.id,
            company_name=comp,
            license_number=lic,
            accepted_materials=mats,
            service_area="Chennai Metropolitan",
            latitude=lat,
            longitude=lon,
            verification_status=verif,
            rating=rat
        )
        db.add(r)
        recyclers.append(r)

    db.commit()

    # 4. 20 Scrap Items
    print("Seeding Scrap Items...")
    categories = ["Plastic", "Paper", "Metal", "E-waste", "Glass", "Mixed waste"]
    qualities = ["Good", "Medium", "Poor"]
    statuses = [ScrapStatus.PENDING, ScrapStatus.MATCHED, ScrapStatus.OFFER_ACCEPTED, ScrapStatus.COMPLETED]

    scrap_items = []
    for i in range(20):
        col = random.choice(collectors)
        cat = random.choice(categories)
        qual = random.choice(qualities)
        status = statuses[i % len(statuses)]
        
        s = ScrapItem(
            collector_id=col.id,
            category=cat,
            predicted_category=cat,
            quality=qual,
            predicted_quality=qual,
            weight=round(random.uniform(5.0, 150.0), 2),
            image_url=f"/static/uploads/scrap_sample_{i+1}.jpg",
            description=f"Batch of scrap material collected from site {i+1}",
            status=status,
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
        )
        db.add(s)
        scrap_items.append(s)

    db.commit()

    # 5. 15 Offers
    print("Seeding Offers...")
    offers = []
    for i in range(15):
        s = scrap_items[i % len(scrap_items)]
        rec = random.choice([r for r in recyclers if any(m in s.category for m in r.accepted_materials)] or recyclers)
        offered_p = round(s.weight * random.uniform(12.0, 45.0), 2)
        
        o = Offer(
            scrap_id=s.id,
            recycler_id=rec.id,
            offered_price=offered_p,
            pickup_available=True,
            estimated_pickup_date=datetime.now(timezone.utc) + timedelta(days=random.randint(1, 4)),
            status=OfferStatus.ACCEPTED if s.status in [ScrapStatus.OFFER_ACCEPTED, ScrapStatus.COMPLETED] else OfferStatus.PENDING,
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 5))
        )
        db.add(o)
        offers.append(o)

    db.commit()

    # 6. 10 Transactions & Recycling Records
    print("Seeding Transactions & Certificates...")
    for i in range(10):
        s = scrap_items[i]
        col = s.collector
        rec = recyclers[i % len(recyclers)]
        
        t = Transaction(
            scrap_id=s.id,
            collector_id=col.id,
            recycler_id=rec.id,
            accepted_price=round(s.weight * 25.0, 2),
            pickup_status=PickupStatus.COMPLETED if i < 7 else PickupStatus.IN_TRANSIT,
            recycling_status=RecyclingStatus.COMPLETED if i < 5 else RecyclingStatus.PROCESSING,
            transaction_date=datetime.now(timezone.utc) - timedelta(days=random.randint(5, 15)),
            completed_at=datetime.now(timezone.utc) if i < 5 else None
        )
        db.add(t)
        db.flush()

        if i < 5:
            rr = RecyclingRecord(
                transaction_id=t.id,
                material_type=s.category,
                weight=s.weight,
                recycling_method="Mechanical shredding & chemical refining",
                completion_date=datetime.now(timezone.utc),
                certificate_reference_number=f"CERT-SIH2026-{1000+i}"
            )
            db.add(rr)

    db.commit()
    db.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
