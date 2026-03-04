"""
sentinel/core/grade.py
----------------------
Grading harness for candidate evaluation.
Compares detected GhostFlags against a ground_truth.json evidence file.
Calculates Precision, Recall, and Financial Variance.
"""

import json
import logging
from dataclasses import dataclass
from typing import List, Dict

logger = logging.getLogger(__name__)

@dataclass
class GradingResult:
    dataset_name: str
    precision: float
    recall: float
    f1_score: float
    financial_variance: float  # (Detected - Expected)
    status: str                # PASS | FAIL (based on tolerance)

def score_candidate(detected_flags: List, ground_truth: Dict) -> GradingResult:
    """
    Scores the reconciliation output against the gold standard.
    ground_truth format: 
    {
        "dataset": "...",
        "expected_flags": [
            {"sku": "...", "type": "...", "impact": 100.0, "lines": [1, 5]}
        ],
        "total_recoverable": 1500.0
    }
    """
    true_positives = 0
    false_positives = 0
    expected_count = len(ground_truth.get("expected_flags", []))
    
    # 1. Map expected flags for quick lookup
    expected_map = {
        (f["sku"], f["type"]): f["impact"] 
        for f in ground_truth.get("expected_flags", [])
    }
    
    # 2. Score detected flags
    detected_total = 0
    for flag in detected_flags:
        key = (flag.sku, flag.ghost_type.value)
        detected_total += flag.financial_impact
        
        if key in expected_map:
            true_positives += 1
            # Optional: check impact variance
            del expected_map[key]
        else:
            false_positives += 1
            
    # 3. Calculate metrics
    fn_count = len(expected_map)  # Remaining items in map were missed
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + fn_count) if (true_positives + fn_count) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    variance = detected_total - ground_truth.get("total_recoverable", 0)
    
    status = "PASS" if f1 > 0.9 and abs(variance) < 1.0 else "FAIL"
    
    return GradingResult(
        dataset_name=ground_truth.get("dataset", "unknown"),
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1_score=round(f1, 4),
        financial_variance=round(variance, 2),
        status=status
    )
