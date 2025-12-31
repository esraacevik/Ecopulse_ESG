"""
ECOLOGIA ML Configuration
=========================

Veri setleri yolları ve model konfigürasyonları
"""

from pathlib import Path
from typing import Dict, List

# Base paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
DATASETS_DIR = PROJECT_ROOT / "yeni_veri_setleri"

# ==============================================================================
# VERİ SETLERİ YOLLARI
# ==============================================================================

DATASETS: Dict[str, Dict] = {
    # ⭐⭐⭐ BİRİNCİL VERİ SETLERİ
    "supply_chain_ghg": {
        "path": DATASETS_DIR / "Supply Chain Greenhouse Gas Emission Factors v1.3 by NAICS-6",
        "files": {
            "co2e": "SupplyChainGHGEmissionFactors_v1.3.0_NAICS_CO2e_USD2022.csv",
            "by_ghg": "SupplyChainGHGEmissionFactors_v1.3.0_NAICS_byGHG_USD2022.csv"
        },
        "priority": 3,
        "models": ["sector_benchmark", "target_recommendation"]
    },
    
    "corporate_environmental": {
        "path": DATASETS_DIR / "Corporate Environmental Impact",
        "files": {
            "full": "final_raw_sample_0_percent.csv",
            "sample": "final_raw_sample_3_percent.csv"
        },
        "priority": 3,
        "models": ["sector_benchmark", "target_recommendation"]
    },
    
    "ember": {
        "path": DATASETS_DIR / "Ember",
        "files": {
            "yearly": "yearly_full_release_long_format.csv"
        },
        "priority": 3,
        "models": ["energy_prediction", "sector_benchmark"]
    },
    
    "eia_hourly": {
        "path": DATASETS_DIR / "US EIA hourly electiricty consumption",
        "files": {
            "dictionary": "data_dictionary.csv",
            "data_dir": "data"  # 90+ CSV files
        },
        "priority": 3,
        "models": ["energy_prediction", "anomaly_detection"]
    },
    
    "building_energy": {
        "path": DATASETS_DIR / "buildingenergydataset",
        "files": {
            "2016_2017": "1.data_20162017.csv",
            "2018": "2.data_2018.csv",
            "2019": "3.data_2019.csv",
            "2020": "4.data_2020.csv",
            "2021": "5.data_2021.csv"
        },
        "priority": 3,
        "models": ["energy_prediction", "anomaly_detection"]
    },
    
    "monthly_energy_sector": {
        "path": DATASETS_DIR / "Monthly and Annual Energy Consumption by Sector",
        "files": {
            "primary": "Table_1.1_Primary_Energy_Overview.xlsx"
        },
        "priority": 3,
        "models": ["energy_prediction", "sector_benchmark"]
    },
    
    # ⭐⭐ İKİNCİL VERİ SETLERİ
    "nyc_building": {
        "path": DATASETS_DIR / "NYC building energy and water data",
        "files": {
            "main": "NYC_Building_Energy_and_Water_Data_Disclosure_for_Local_Law_84_2023_to_Present__Data_for_Calendar_Year_2022-Present_.csv"
        },
        "priority": 2,
        "models": ["energy_prediction", "anomaly_detection", "sector_benchmark"],
        "note": "Large file (>200MB), use chunked reading"
    },
    
    "world_weather": {
        "path": DATASETS_DIR / "World Weather Repository ( Daily Updating )",
        "files": {
            "csv": "GlobalWeatherRepository.csv",
            "db": "state.db"
        },
        "priority": 2,
        "models": ["energy_prediction"]
    },
    
    "epa_vehicle": {
        "path": DATASETS_DIR / "EPA Vehicle Fuel Economy",
        "files": {
            "vehicles": "vehicles.csv"
        },
        "priority": 2,
        "models": ["target_recommendation"]
    },
    
    "epa_egrid": {
        "path": DATASETS_DIR / "EPA eGRID",
        "files": {
            "main": "egrid2023_data_rev2.xlsx"
        },
        "priority": 2,
        "models": ["sector_benchmark", "target_recommendation"]
    },
    
    "recs": {
        "path": DATASETS_DIR / "Residential Energy Consumption Survey (RECS) Files",
        "files": {
            "2015": "recs2015_public_v4.csv"
        },
        "priority": 2,
        "models": ["energy_prediction"]
    },
    
    "building_benchmark": {
        "path": DATASETS_DIR / "Building Energy Benchmarking Data",
        "files": {
            "main": "Building_Energy_Benchmarking_Data,_2015-Present_20251226.csv"
        },
        "priority": 2,
        "models": ["sector_benchmark"]
    },
    
    # ⭐ OPSİYONEL VERİ SETLERİ
    "ashrae": {
        "path": DATASETS_DIR / "ASHRAE Global Thermal Comfort Database II",
        "files": {
            "main": "ashrae_db2.01.csv"
        },
        "priority": 1,
        "models": ["energy_prediction"]
    },
    
    "occupancy": {
        "path": DATASETS_DIR / "Occupancy Detection Dataset",
        "files": {
            "train": "DataTraining.csv",
            "test": "DataTest.csv"
        },
        "priority": 1,
        "models": ["energy_prediction"]
    }
}

# ==============================================================================
# MODEL KONFİGÜRASYONLARI
# ==============================================================================

MODEL_CONFIGS: Dict[str, Dict] = {
    "energy_prediction": {
        "name": "Energy Prediction Model",
        "description": "Geçmiş tüketimden gelecek enerji tüketimi tahmini",
        "algorithms": ["lstm", "prophet", "xgboost", "random_forest"],
        "default_algorithm": "xgboost",
        "metrics": ["mae", "rmse", "mape", "r2"],
        "target_mape": 0.10,  # < 10%
        "features": {
            "time": ["hour", "day_of_week", "month", "is_weekend", "is_holiday", "season"],
            "lag": ["lag_1h", "lag_24h", "lag_168h"],
            "rolling": ["rolling_mean_24h", "rolling_std_24h"],
            "weather": ["temperature", "humidity", "cdd", "hdd"]
        }
    },
    
    "anomaly_detection": {
        "name": "Anomaly Detection Model",
        "description": "Olağandışı tüketim/emisyon tespiti",
        "algorithms": ["isolation_forest", "one_class_svm", "autoencoder", "statistical"],
        "default_algorithm": "isolation_forest",
        "metrics": ["precision", "recall", "f1_score", "auc"],
        "target_f1": 0.85,
        "contamination": 0.05,  # Expected anomaly ratio
        "anomaly_types": ["spike", "drop", "trend_deviation", "seasonal_anomaly"]
    },
    
    "sector_benchmark": {
        "name": "Sector Benchmarking Model",
        "description": "Sektör karşılaştırma ve şirket konumlandırma",
        "algorithms": ["kmeans", "dbscan", "percentile_ranking"],
        "default_algorithm": "percentile_ranking",
        "metrics": ["sector_coverage", "cluster_quality"],
        "n_clusters": 5,
        "rating_scale": ["A", "B", "C", "D", "F"],
        "benchmark_metrics": ["emission_intensity", "energy_intensity", "renewable_ratio"]
    },
    
    "target_recommendation": {
        "name": "Target Recommendation Model",
        "description": "Net zero hedef ve azaltım planı önerisi",
        "algorithms": ["linear_regression", "scenario_modeling", "optimization"],
        "default_algorithm": "scenario_modeling",
        "target_years": [2030, 2040, 2050],
        "sbti_aligned": True,
        "reduction_actions": {
            "scope1": ["fleet_electrification", "fuel_switching", "efficiency"],
            "scope2": ["renewable_energy", "energy_efficiency", "ppa"],
            "scope3": ["supplier_engagement", "travel_reduction", "logistics"]
        }
    }
}

# ==============================================================================
# EĞİTİM PARAMETRELERİ
# ==============================================================================

TRAINING_CONFIG = {
    "test_size": 0.2,
    "val_size": 0.1,
    "random_state": 42,
    "n_folds": 5,
    "early_stopping_rounds": 50,
    "max_trials": 100,  # Optuna trials
    
    "xgboost_params": {
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.1,
        "min_child_weight": 1,
        "subsample": 0.8,
        "colsample_bytree": 0.8
    },
    
    "lstm_params": {
        "units": 64,
        "layers": 2,
        "dropout": 0.2,
        "epochs": 100,
        "batch_size": 32,
        "patience": 10
    },
    
    "isolation_forest_params": {
        "n_estimators": 100,
        "max_samples": "auto",
        "contamination": 0.05,
        "random_state": 42
    }
}

# ==============================================================================
# YARDIMCI FONKSİYONLAR
# ==============================================================================

def get_dataset_path(dataset_name: str, file_key: str = None) -> Path:
    """Veri seti yolunu döndür"""
    if dataset_name not in DATASETS:
        raise ValueError(f"Unknown dataset: {dataset_name}")
    
    ds = DATASETS[dataset_name]
    base_path = ds["path"]
    
    if file_key:
        if file_key not in ds["files"]:
            raise ValueError(f"Unknown file key: {file_key}")
        return base_path / ds["files"][file_key]
    
    return base_path


def get_datasets_for_model(model_name: str) -> List[str]:
    """Bir model için kullanılacak veri setlerini döndür"""
    return [
        name for name, config in DATASETS.items()
        if model_name in config.get("models", [])
    ]


def get_high_priority_datasets() -> List[str]:
    """Yüksek öncelikli veri setlerini döndür"""
    return [
        name for name, config in DATASETS.items()
        if config.get("priority", 0) >= 3
    ]

