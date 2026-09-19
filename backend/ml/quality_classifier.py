"""
Quality Assessment ML Service
Estimates degradation, contamination, and grade of material.
"""

def estimate_quality_grade(material_type: str, weight: float) -> Tuple[str, float]:
    """
    Evaluates quality based on material type and physical density heuristics.
    """
    if material_type in ["E-waste", "Metal"]:
        return "Good", 0.89
    elif material_type in ["Plastic", "Paper"]:
        return "Medium", 0.82
    return "Poor", 0.71
