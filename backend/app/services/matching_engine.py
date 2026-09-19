"""
Multi-Factor Recycler Matching & Rule-Based Recommendation Algorithm
Combines rule-based filters with multi-factor weighted scoring.
"""
import math
from typing import List, Dict, Any
from app.models.models import Recycler, ScrapItem

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine formula to compute geographical distance between two coordinate pairs."""
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def match_recyclers_for_scrap(scrap: ScrapItem, recyclers: List[Recycler], collector_lat: float, collector_lon: float) -> List[Dict[str, Any]]:
    recommendations = []

    for recycler in recyclers:
        # --- RULE-BASED VALIDATION (Mandatory Criteria) ---
        if not recycler.verification_status:
            continue # Exclude unverified recyclers from algorithmic matching
        
        # Check material capability
        material_match_flag = any(mat.lower() == scrap.category.lower() for mat in recycler.accepted_materials)
        if not material_match_flag:
            continue # Must accept category

        # --- MULTI-FACTOR SCORE CALCULATION ---
        
        # 1. Material Score (100% if exact match)
        material_score = 100.0

        # 2. Distance Score (Decays as distance increases up to 50 km)
        dist_km = calculate_distance_km(collector_lat, collector_lon, recycler.latitude, recycler.longitude)
        distance_score = max(0.0, 100.0 - (dist_km * 2.0))

        # 3. Price Score (Simulated competitive score based on historical rating & material)
        price_score = min(100.0, 70.0 + (recycler.rating * 6.0))

        # 4. Verification Score (100% since unverified are filtered out)
        verification_score = 100.0 if recycler.verification_status else 0.0

        # 5. Availability Score
        availability_score = 90.0

        # 6. Rating Score (Normalized out of 100)
        rating_score = (recycler.rating / 5.0) * 100.0

        # Formula: Weighted Sum
        final_match_score = (
            (material_score * 0.30) +
            (distance_score * 0.20) +
            (price_score * 0.20) +
            (verification_score * 0.15) +
            (availability_score * 0.10) +
            (rating_score * 0.05)
        )

        explanation = (
            f"Recommended due to 100% material compatibility ({scrap.category}), "
            f"proximity ({round(dist_km, 1)} km away), high reliability rating ({recycler.rating}/5.0), "
            f"and verified accreditation status."
        )

        recommendations.append({
            "recycler": recycler,
            "match_score": round(final_match_score, 1),
            "breakdown": {
                "material_match": round(material_score, 1),
                "distance_score": round(distance_score, 1),
                "price_score": round(price_score, 1),
                "verification_score": round(verification_score, 1),
                "availability_score": round(availability_score, 1),
                "rating_score": round(rating_score, 1)
            },
            "explanation": explanation
        })

    # Sort descending by match score
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations
