"""
Model Training Utilities
========================

Model eğitim, değerlendirme ve serileştirme fonksiyonları
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, Any, List
from pathlib import Path
import joblib
import json
from datetime import datetime


def train_test_split_temporal(
    df: pd.DataFrame,
    date_column: str,
    test_size: float = 0.2,
    val_size: float = 0.1
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Zaman serisi için temporal train/val/test split
    
    Args:
        df: DataFrame
        date_column: Tarih kolonu
        test_size: Test oranı
        val_size: Validation oranı
    
    Returns:
        (train_df, val_df, test_df)
    """
    df = df.sort_values(date_column).reset_index(drop=True)
    
    n = len(df)
    test_idx = int(n * (1 - test_size))
    val_idx = int(n * (1 - test_size - val_size))
    
    train_df = df.iloc[:val_idx]
    val_df = df.iloc[val_idx:test_idx]
    test_df = df.iloc[test_idx:]
    
    return train_df, val_df, test_df


def cross_validate_timeseries(
    model,
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = 5,
    gap: int = 0
) -> Dict[str, List[float]]:
    """
    Time series cross-validation
    
    Args:
        model: Sklearn-uyumlu model
        X: Feature DataFrame
        y: Target Series
        n_splits: Fold sayısı
        gap: Train ve test arası boşluk
    
    Returns:
        CV sonuçları
    """
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    
    tscv = TimeSeriesSplit(n_splits=n_splits, gap=gap)
    
    results = {
        "mae": [],
        "rmse": [],
        "r2": [],
        "mape": []
    }
    
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        results["mae"].append(mean_absolute_error(y_test, y_pred))
        results["rmse"].append(np.sqrt(mean_squared_error(y_test, y_pred)))
        results["r2"].append(r2_score(y_test, y_pred))
        
        # MAPE (avoiding division by zero)
        mask = y_test != 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100
            results["mape"].append(mape)
    
    return results


def evaluate_regression(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """
    Regresyon model değerlendirmesi
    
    Args:
        y_true: Gerçek değerler
        y_pred: Tahmin değerleri
    
    Returns:
        Metrik dictionary
    """
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    # MAPE
    mask = y_true != 0
    if mask.sum() > 0:
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    else:
        mape = np.nan
    
    return {
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "mape": mape
    }


def evaluate_classification(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    Sınıflandırma model değerlendirmesi
    
    Args:
        y_true: Gerçek etiketler
        y_pred: Tahmin etiketler
        y_proba: Tahmin olasılıkları (opsiyonel)
    
    Returns:
        Metrik dictionary
    """
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score,
        f1_score, roc_auc_score
    )
    
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average="weighted", zero_division=0),
        "recall": recall_score(y_true, y_pred, average="weighted", zero_division=0),
        "f1": f1_score(y_true, y_pred, average="weighted", zero_division=0)
    }
    
    if y_proba is not None:
        try:
            if len(np.unique(y_true)) == 2:
                metrics["auc"] = roc_auc_score(y_true, y_proba[:, 1])
            else:
                metrics["auc"] = roc_auc_score(y_true, y_proba, multi_class="ovr")
        except:
            metrics["auc"] = np.nan
    
    return metrics


def save_model(
    model: Any,
    path: Path,
    metadata: Optional[Dict] = None
) -> None:
    """
    Modeli kaydet
    
    Args:
        model: Eğitilmiş model
        path: Kayıt yolu
        metadata: Ek metadata (opsiyonel)
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save model
    joblib.dump(model, path)
    
    # Save metadata
    if metadata:
        metadata["saved_at"] = datetime.now().isoformat()
        metadata_path = path.with_suffix(".json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)


def load_model(path: Path) -> Tuple[Any, Optional[Dict]]:
    """
    Modeli yükle
    
    Args:
        path: Model yolu
    
    Returns:
        (model, metadata)
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {path}")
    
    model = joblib.load(path)
    
    # Load metadata if exists
    metadata_path = path.with_suffix(".json")
    metadata = None
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    
    return model, metadata


def get_feature_importance(
    model: Any,
    feature_names: List[str]
) -> pd.DataFrame:
    """
    Model feature importance'ını al
    
    Args:
        model: Eğitilmiş model
        feature_names: Özellik isimleri
    
    Returns:
        Feature importance DataFrame
    """
    if hasattr(model, "feature_importances_"):
        importance = model.feature_importances_
    elif hasattr(model, "coef_"):
        importance = np.abs(model.coef_).flatten()
    else:
        raise ValueError("Model does not have feature importance")
    
    return pd.DataFrame({
        "feature": feature_names,
        "importance": importance
    }).sort_values("importance", ascending=False).reset_index(drop=True)


def hyperparameter_tuning(
    model_class,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    param_grid: Dict,
    n_trials: int = 100,
    cv_splits: int = 5,
    metric: str = "rmse"
) -> Dict:
    """
    Optuna ile hyperparameter tuning
    
    Args:
        model_class: Model sınıfı
        X_train: Eğitim feature'ları
        y_train: Eğitim target'ı
        param_grid: Parametre aralıkları
        n_trials: Deneme sayısı
        cv_splits: CV fold sayısı
        metric: Optimize edilecek metrik
    
    Returns:
        En iyi parametreler
    """
    import optuna
    from sklearn.model_selection import cross_val_score
    
    def objective(trial):
        params = {}
        for key, value in param_grid.items():
            if isinstance(value, tuple) and len(value) == 3:
                if value[2] == "int":
                    params[key] = trial.suggest_int(key, value[0], value[1])
                elif value[2] == "float":
                    params[key] = trial.suggest_float(key, value[0], value[1])
                elif value[2] == "log":
                    params[key] = trial.suggest_float(key, value[0], value[1], log=True)
            elif isinstance(value, list):
                params[key] = trial.suggest_categorical(key, value)
        
        model = model_class(**params)
        
        if metric == "rmse":
            scores = cross_val_score(model, X_train, y_train, 
                                    cv=cv_splits, scoring="neg_root_mean_squared_error")
            return -scores.mean()
        elif metric == "mae":
            scores = cross_val_score(model, X_train, y_train,
                                    cv=cv_splits, scoring="neg_mean_absolute_error")
            return -scores.mean()
        elif metric == "r2":
            scores = cross_val_score(model, X_train, y_train,
                                    cv=cv_splits, scoring="r2")
            return scores.mean()
    
    study = optuna.create_study(
        direction="minimize" if metric in ["rmse", "mae"] else "maximize"
    )
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
    
    return {
        "best_params": study.best_params,
        "best_value": study.best_value,
        "n_trials": len(study.trials)
    }


def create_ensemble_predictions(
    models: List[Any],
    X: pd.DataFrame,
    weights: Optional[List[float]] = None,
    method: str = "average"
) -> np.ndarray:
    """
    Ensemble tahminleri oluştur
    
    Args:
        models: Model listesi
        X: Feature DataFrame
        weights: Model ağırlıkları
        method: "average" veya "weighted"
    
    Returns:
        Ensemble tahminleri
    """
    predictions = np.array([model.predict(X) for model in models])
    
    if method == "average":
        return predictions.mean(axis=0)
    
    elif method == "weighted":
        if weights is None:
            weights = [1/len(models)] * len(models)
        weights = np.array(weights).reshape(-1, 1)
        return (predictions * weights).sum(axis=0)
    
    else:
        raise ValueError(f"Unknown method: {method}")

