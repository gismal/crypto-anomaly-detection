import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict,Any, List, Tuple, Optional
from src.config import CONTAMINATION, logger

class AnomalyDetector:
    """
    Detects anomalies in real time crypto data using Isolation Forest
    Includes features for initial warm up, periodic retraining (concept drift), anomaly scoreoutput and basic
    feature importance explanation (XAI)
    """
    
    def __init__(self, contamination: float = CONTAMINATION, warmup_period: int = 100, retrain_interval: int = 100):
         """
         Args:
            - contamination: Expected proportion of anomalies in the data
            - warmup_period: Minimum data points required for initial training
            - retrain_interval: Number of predictions before retraining the model
         """
         self.contamination = contamination
         self.warmup_period = warmup_period
         self.retrain_interval  = retrain_interval
         self.model = IsolationForest(contamination = self.contamination, random_state = 42)
         
         # sliding buffer to hold the historical vectors for training and retraining
         self.buffer: List[List[float]] = []
         self.is_ready = False
         self.prediction_count = 0
         
         # exact order of features matches the vector format
         self.feature_names = [
             "rolling_mean", "rolling_std", "price_change", "z_score", "pct_change", "high_low_spread"
         ]
         
    
    def _extract_vector(self, features: Dict[str, float]) -> List[float]:
        """ Flattens the feature dictionary into a list based on a strict order"""
        return [features[name] for name in self.feature_names]
    
    def _explain_anomaly(self, vector: List[float]) -> str:
        """ XAI: Identifies which feature deviated most from the buffer mean """
        if not self.buffer:
            return "Unknown"
        
        matrix = np.array(self.buffer)
        means = np.mean(matrix, axis = 0)
        stds = np.std(matrix, axis = 0) + 1e-8
        
        # Calculate absolute Z-scores relative to training history
        z_scores = np.abs((np.array(vector) - means) / stds)
        max_idx = int(np.argmax(z_scores))
        
        return self.feature_names[max_idx]    
    
    def train_or_predict(self, features: Dict[str, float]) -> Tuple[int, float, Optional[str]]:
        """
        Processes live features. Trains during warm up, predicts when ready
        
        Returns:
            Tuple[,nt, float, Optional[str]]:
                - Prediction (1: Normal, -1: Anomaly)
                - Anomaly Score (Lower values mean more anomalous)
                - Reason (Feature name that caused the anomaly, or None)
        """
        vector = self._extract_vector(features)
        
        # Warm up phase
        if not self.is_ready:
            self.buffer.append(vector)
            if len(self.buffer) >= self.warmup_period:
                logger.info(f"Training initial model with {self.warmup_period} data points...")
                self.model.fit(self.buffer)
                self.is_ready = True
                logger.info("Model training complete. Live predictions active")
                
            return 1, 0.0, None
        
        """
        Predict using the training model decision_function returns negative values for anomalies, positive for normal points
        """
        score = float(self.model.decision_function([vector])[0])
        prediction = int(self.model.predict([vector])[0])
        
        reason = None
        if prediction == -1:
            reason = self._explain_anomaly(vector)
            logger.warning(f"ANOMALY! Triggered by extreme: {reason}  | Score: {score:.4f}")
            
        # Store current data point to maintain dynamic memory for retraining
        self.buffer.append(vector)
        self.prediction_count += 1
        
        # Concept Drift Managment: Periodic Retraining
        if self.prediction_count % self.retrain_interval == 0:
            logger.info(f"Retraining model to adapt to recent market drift (Count: {self.prediction_count})...")
            # Keep buffer size optimal to precent memory leaks (keep last 2000 points)
            if len(self.buffer) > 2000:
                self.buffer = self.buffer[-2000:]
            self.model.fit(self.buffer)
        
        return prediction, score, reason        

        
              
        
         
    