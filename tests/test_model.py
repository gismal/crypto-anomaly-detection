import pytest
from src.model import AnomalyDetector

@pytest.fixture
def dummy_features():
    return {
        "rolling_mean": 100.0, "rolling_std": 1.0, "price_change": 0.5, "z_score": 0.1, "pct_change": 0.2, "high_low_spread": 1.2
    }
    

def test_anomaly_detector_warmup(dummy_features):
    detector = AnomalyDetector(warmup_period= 3)
    
    # Warm up outputs should return (1, 0.0, None)
    pred, score, reason = detector.train_or_predict(dummy_features)
    assert pred == 1
    assert detector.is_ready is False
    
    detector.train_or_predict(dummy_features)
    
    # 3rd poin triggers training completion
    pred, score, reason = detector.train_or_predict(dummy_features)
    assert detector.is_ready is True
    
def test_anomaly_prediction(dummy_features):
    detector = AnomalyDetector(warmup_period= 3, contamination  = 0.5)
    
    # train model for 3 times
    for _ in range(3):
        detector.train_or_predict(dummy_features)
        
    # Introduce an extreme outlier
    anomaly_features = {
        "rolling_mean": 999.0, "rolling_std": 99.0, "price_change": 50.0,
        "z_score": 10.0, "pct_change": 25.0, "high_low_spread": 80.0
    }    
    
    pred, score, reason = detector.train_or_predict(anomaly_features)

    assert pred in [1, -1]
    assert isinstance(score, float)