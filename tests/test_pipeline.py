import pytest
from unittest.mock import patch
from src.pipeline import main

# mocks
@patch("src.pipeline.DiscordNotifier")
@patch("src.pipeline.CSVLogger")
@patch("src.pipeline.AnomalyDetector")
@patch("src.pipeline.FeatureEngine")
@patch("src.pipeline.BinanceStreamer")
def test_pipeline_anomaly_flow(MockStreamer, MockEngine, MockDetector, MockCSV, MockNotifier):
    """
    Sets a syntetic environment to test the pipeline by mocking a anomaly flow
    
    params:
        - MockStreamer: 
        - MockEngine:
        - MockDetector:
        - MockCSV:
        - MockNotifier:
    """
    streamer_instance = MockStreamer.return_value
    engine_instance = MockEngine.return_value
    detector_instance = MockDetector.return_value
    csv_instance = MockCSV.return_value
    notifier_instance = MockNotifier.return_value
    
    # Mock instances to break the while loop
    streamer_instance.get_next.side_effect = [
        {"price": 750000.0},
        KeyboardInterrupt()
    ]
    
    # Give the instance not without waiting 60 secs
    engine_instance.get_current_features.return_value = {"z_score": 5.0}
    
    # Model acts like it finds an anomaly 
    detector_instance.train_or_predict.return_value = (-1, 0.99, "Z-Score Peak")
    
    main()
    
    # Tests the notifier if it notifies
    notifier_instance.send_alert.assert_called_once_with(750000.0, "Z-Score Peak", 0.99)
    
    # Does CSV save
    csv_instance.log.assert_called_once()
    
    # If stop works
    streamer_instance.stop.assert_called_once()
