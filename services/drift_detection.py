import difflib

def detect_schema_drift(expected_columns: list, actual_columns: list, threshold: float = 0.8) -> dict:
    """
    Compares expected vs actual columns. 
    Returns a report with missing, extra, and fuzzy matches.
    """
    missing = [col for col in expected_columns if col not in actual_columns]
    extra = [col for col in actual_columns if col not in expected_columns]
    
    matches = []
    
    for m_col in missing:
        # Find best match in extra columns
        best_match = None
        best_score = 0.0
        
        for e_col in extra:
            score = difflib.SequenceMatcher(None, m_col.lower(), e_col.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = e_col
        
        if best_score >= threshold:
            matches.append({
                "expected": m_col,
                "actual": best_match,
                "confidence": round(best_score, 2)
            })

    drift_detected = len(missing) > 0 or len(extra) > 0
    
    return {
        "drift_detected": drift_detected,
        "missing": missing,
        "extra": extra,
        "matches": matches
    }
