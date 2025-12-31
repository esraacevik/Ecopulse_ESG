"""
Energy Prediction Model
=======================

Geçmiş tüketim verilerinden gelecek enerji tüketimini tahmin eder.

Algoritmalar:
- LSTM: Long Short-Term Memory
- Prophet: Facebook Prophet
- XGBoost: Gradient Boosting
- Random Forest: Ensemble

Kullanım:
    from models.energy_prediction import EnergyPredictor
    
    predictor = EnergyPredictor(algorithm="xgboost")
    predictor.train(train_data)
    predictions = predictor.predict(test_data)
"""

__all__ = [
    "EnergyPredictor",
    "LSTMModel",
    "ProphetModel", 
    "XGBoostModel"
]

