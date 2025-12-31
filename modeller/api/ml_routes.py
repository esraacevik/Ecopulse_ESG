"""
ML API Routes
==============

Machine Learning modelleri için FastAPI endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import sys
from pathlib import Path
import xgboost as xgb

# Modeller path'ine ekle
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Backend path'ine ekle (AI servisleri için)
backend_path = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from models.anomaly_detection.detector import AnomalyDetector
from models.sector_benchmark.benchmarker import SectorBenchmarker
from models.target_recommendation.recommender import TargetRecommender
from models.energy_prediction.predictor import EnergyPredictor
from models.energy_prediction.data_loader import EnergyDataLoader

# AI servisleri
try:
    from app.services.qwen_ml_service import QwenMLAdvisor
    _ml_advisor = None
    
    def get_ml_advisor():
        global _ml_advisor
        if _ml_advisor is None:
            _ml_advisor = QwenMLAdvisor()
        return _ml_advisor
except ImportError:
    print("[WARNING] QwenMLAdvisor import edilemedi, AI önerileri devre dışı")
    _ml_advisor = None
    
    def get_ml_advisor():
        return None

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# Model instance'ları (lazy loading)
_benchmarker = None
_recommender = None
_anomaly_detector = None
_energy_predictor = None


def get_benchmarker():
    global _benchmarker
    if _benchmarker is None:
        _benchmarker = SectorBenchmarker(verbose=False)
        _benchmarker.load_data()
    return _benchmarker


def get_recommender():
    global _recommender
    if _recommender is None:
        _recommender = TargetRecommender(verbose=False)
    return _recommender


def get_energy_predictor(location: str = "Istanbul,TR", include_weather: bool = True):
    """
    Get or create energy predictor instance
    
    Tries to load from checkpoint first, creates new if not available.
    """
    global _energy_predictor
    
    # Check if we have a cached predictor for this location
    cache_key = f"{location}_{include_weather}"
    if _energy_predictor is not None and hasattr(_energy_predictor, '_cache_key'):
        if _energy_predictor._cache_key == cache_key and _energy_predictor.is_trained:
            return _energy_predictor
    
    # Try to load from trained model checkpoint
    predictor = load_trained_model(location, include_weather)
    
    if predictor is None:
        # No trained model found, create new instance
        predictor = EnergyPredictor(
            algorithm="xgboost",
            location=location,
            include_weather=include_weather
        )
    
    # Cache the predictor
    predictor._cache_key = cache_key
    _energy_predictor = predictor
    
    return predictor


def load_trained_model(location: str = "Istanbul,TR", include_weather: bool = True) -> Optional[EnergyPredictor]:
    """
    Load trained model from checkpoint or final model directory
    
    Returns:
        EnergyPredictor instance if found, None otherwise
    """
    from pathlib import Path
    
    # Try final model directory first (most reliable)
    model_path = Path(__file__).parent.parent / "outputs" / "models" / "weather_energy_model"
    
    if model_path.exists() and (model_path / "config.json").exists():
        try:
            predictor = EnergyPredictor(
                algorithm="xgboost",
                location=location,
                include_weather=include_weather
            )
            predictor.load(model_path)
            
            if predictor.is_trained:
                print(f"[INFO] Model loaded from: {model_path}")
                return predictor
        except Exception as e:
            print(f"[WARNING] Failed to load model from {model_path}: {e}")
    
    # Try checkpoint directory as fallback
    checkpoint_dir = Path(__file__).parent.parent / "checkpoints" / "weather_training"
    model_checkpoint = checkpoint_dir / "model_checkpoint.json"
    
    if model_checkpoint.exists():
        try:
            # Load from checkpoint requires special handling
            # We need to reconstruct the predictor with data
            predictor = EnergyPredictor(
                algorithm="xgboost",
                location=location,
                include_weather=include_weather
            )
            
            # Load checkpoint state
            import json
            with open(checkpoint_dir / "training_state.json", "r") as f:
                state = json.load(f)
            
            # Load model from checkpoint
            import xgboost as xgb
            bst = xgb.Booster()
            bst.load_model(str(model_checkpoint))
            
            # Wrap in XGBRegressor
            predictor.model.model = xgb.XGBRegressor()
            predictor.model.model._Booster = bst
            predictor.model.is_fitted = True
            predictor.model.feature_names = state.get("feature_columns", [])
            predictor.feature_engineer.feature_columns = state.get("feature_columns", [])
            predictor.is_trained = True
            
            print(f"[INFO] Model loaded from checkpoint: {checkpoint_dir}")
            return predictor
        except Exception as e:
            print(f"[WARNING] Failed to load model from checkpoint: {e}")
    
    return None


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class BenchmarkRequest(BaseModel):
    """Sektör benchmark isteği"""
    company_name: str = Field(..., description="Şirket adı")
    naics_code: Optional[str] = Field(None, description="NAICS sektör kodu")
    sector: Optional[str] = Field(None, description="Sektör adı")
    total_emissions: float = Field(..., description="Toplam emisyon (ton CO2e)")
    revenue: float = Field(..., description="Gelir (USD)")
    employees: Optional[int] = Field(None, description="Çalışan sayısı")


class BenchmarkResponse(BaseModel):
    """Sektör benchmark yanıtı"""
    success: bool
    company: str
    sector: Optional[str]
    metrics: Optional[Dict]
    interpretation: Optional[str]
    error: Optional[str] = None


class TargetRequest(BaseModel):
    """Net zero hedef isteği"""
    company_name: str = Field(..., description="Şirket adı")
    scope1_emissions: float = Field(0, description="Scope 1 emisyon (ton CO2e)")
    scope2_emissions: float = Field(0, description="Scope 2 emisyon (ton CO2e)")
    scope3_emissions: float = Field(0, description="Scope 3 emisyon (ton CO2e)")
    base_year: int = Field(2024, description="Baz yıl")
    target_year: int = Field(2030, description="Hedef yıl")
    ambition: str = Field("1.5C", description="Hedef seviyesi: 1.5C, well_below_2C, 2C")


class TargetResponse(BaseModel):
    """Net zero hedef yanıtı"""
    success: bool
    summary: Optional[Dict]
    milestones: Optional[List[Dict]]
    scope_strategies: Optional[Dict]
    investment: Optional[Dict]
    error: Optional[str] = None


class AnomalyRequest(BaseModel):
    """Anomali tespit isteği"""
    data: List[Dict] = Field(..., description="Veri noktaları")
    columns: Optional[List[str]] = Field(None, description="Kontrol edilecek kolonlar")
    contamination: float = Field(0.05, description="Beklenen anomali oranı")


class AnomalyResponse(BaseModel):
    """Anomali tespit yanıtı"""
    success: bool
    total_samples: int
    anomaly_count: int
    anomaly_ratio: float
    anomalies: Optional[List[int]] = None
    error: Optional[str] = None


class SectorListResponse(BaseModel):
    """Sektör listesi yanıtı"""
    success: bool
    sectors: List[Dict]
    total_count: int


class ForecastRequest(BaseModel):
    """Enerji tahmin isteği"""
    data: List[Dict] = Field(..., description="Geçmiş enerji tüketim verisi")
    future_hours: int = Field(24, description="Tahmin edilecek saat sayısı")
    location: str = Field("Istanbul,TR", description="Lokasyon (weather için)")
    lat: Optional[float] = Field(None, description="Enlem (opsiyonel)")
    lon: Optional[float] = Field(None, description="Boylam (opsiyonel)")
    include_weather: bool = Field(True, description="Weather features kullan")


class ForecastResponse(BaseModel):
    """Enerji tahmin yanıtı"""
    success: bool
    predictions: Optional[List[Dict]] = None
    weather_features: Optional[bool] = None
    error: Optional[str] = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/health")
async def ml_health():
    """ML API sağlık kontrolü"""
    return {
        "status": "healthy",
        "models": {
            "sector_benchmark": "available",
            "target_recommendation": "available",
            "anomaly_detection": "available",
            "energy_prediction": "available (requires training)"
        }
    }


@router.post("/benchmark", response_model=BenchmarkResponse)
async def benchmark_company(request: BenchmarkRequest):
    """
    Şirketi sektör ortalamasıyla karşılaştır
    
    NAICS kodu veya sektör adı ile şirketin emisyon yoğunluğunu
    sektör ortalamasıyla karşılaştırır ve rating verir.
    """
    try:
        benchmarker = get_benchmarker()
        
        company_data = {
            "name": request.company_name,
            "total_emissions": request.total_emissions,
            "revenue": request.revenue
        }
        
        if request.naics_code:
            company_data["naics_code"] = request.naics_code
        if request.sector:
            company_data["sector"] = request.sector
        if request.employees:
            company_data["employees"] = request.employees
        
        result = benchmarker.benchmark_company(company_data)
        
        return BenchmarkResponse(
            success=result.get("success", False),
            company=result.get("company", request.company_name),
            sector=result.get("sector"),
            metrics=result.get("metrics"),
            interpretation=result.get("interpretation"),
            error=result.get("error")
        )
    
    except Exception as e:
        return BenchmarkResponse(
            success=False,
            company=request.company_name,
            sector=None,
            metrics=None,
            interpretation=None,
            error=str(e)
        )


@router.post("/target", response_model=TargetResponse)
async def generate_target_pathway(request: TargetRequest):
    """
    Net zero hedef ve yol haritası oluştur
    
    SBTi uyumlu azaltım hedefleri, milestone'lar ve
    scope bazlı stratejiler önerir.
    """
    try:
        recommender = get_recommender()
        
        company_data = {
            "name": request.company_name,
            "scope1_emissions": request.scope1_emissions,
            "scope2_emissions": request.scope2_emissions,
            "scope3_emissions": request.scope3_emissions,
            "base_year": request.base_year
        }
        
        pathway = recommender.generate_pathway(
            company_data,
            target_year=request.target_year,
            ambition=request.ambition
        )
        
        investment = recommender.estimate_investment(pathway, company_data)
        
        return TargetResponse(
            success=True,
            summary={
                "company": pathway["company"],
                "current_emissions": pathway["current_emissions"],
                "target_year": pathway["target_year"],
                "target_emissions": pathway["target_emissions"],
                "total_reduction": f"{pathway['total_reduction']}%",
                "sbti_aligned": pathway["sbti_aligned"]
            },
            milestones=pathway["milestones"],
            scope_strategies=pathway["scope_strategies"],
            investment=investment
        )
    
    except Exception as e:
        return TargetResponse(
            success=False,
            summary=None,
            milestones=None,
            scope_strategies=None,
            investment=None,
            error=str(e)
        )


@router.post("/anomaly", response_model=AnomalyResponse)
async def detect_anomalies(request: AnomalyRequest):
    """
    Verideki anomalileri tespit et
    
    Enerji tüketimi veya emisyon verilerinde
    olağandışı değerleri tespit eder.
    """
    try:
        import pandas as pd
        
        df = pd.DataFrame(request.data)
        
        if len(df) < 10:
            return AnomalyResponse(
                success=False,
                total_samples=len(df),
                anomaly_count=0,
                anomaly_ratio=0,
                error="En az 10 veri noktası gerekli"
            )
        
        detector = AnomalyDetector(
            algorithm="isolation_forest",
            contamination=request.contamination
        )
        
        detector.fit(df, columns=request.columns, verbose=False)
        predictions = detector.detect(df)
        
        anomaly_indices = [i for i, p in enumerate(predictions) if p == -1]
        
        return AnomalyResponse(
            success=True,
            total_samples=len(df),
            anomaly_count=len(anomaly_indices),
            anomaly_ratio=len(anomaly_indices) / len(df),
            anomalies=anomaly_indices
        )
    
    except Exception as e:
        return AnomalyResponse(
            success=False,
            total_samples=0,
            anomaly_count=0,
            anomaly_ratio=0,
            error=str(e)
        )


@router.get("/sectors", response_model=SectorListResponse)
async def get_sectors():
    """
    Mevcut sektör listesini döndür
    
    Benchmark için kullanılabilecek NAICS sektörlerini listeler.
    """
    try:
        benchmarker = get_benchmarker()
        sectors = benchmarker.get_sector_list()
        
        return SectorListResponse(
            success=True,
            sectors=sectors[:50],  # İlk 50 sektör
            total_count=len(sectors)
        )
    
    except Exception as e:
        return SectorListResponse(
            success=False,
            sectors=[],
            total_count=0
        )


@router.get("/sbti-targets")
async def get_sbti_targets():
    """SBTi hedef seviyeleri"""
    return {
        "targets": [
            {
                "id": "1.5C",
                "name": "1.5°C Uyumlu",
                "annual_reduction": "4.2%",
                "description": "En iddialı hedef, Paris Anlaşması uyumlu"
            },
            {
                "id": "well_below_2C",
                "name": "2°C Altı",
                "annual_reduction": "2.5%",
                "description": "Orta seviye hedef"
            },
            {
                "id": "2C",
                "name": "2°C Uyumlu",
                "annual_reduction": "1.5%",
                "description": "Temel hedef"
            }
        ]
    }


@router.post("/forecast", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest):
    """
    Enerji tüketimi tahmini yap
    
    Geçmiş enerji tüketim verilerinden gelecek tüketimi tahmin eder.
    Weather features ile daha doğru tahmin yapar.
    
    Önce eğitilmiş modeli checkpoint'ten yüklemeyi dener.
    Model yoksa veya veri uyumsuzsa yeni eğitim yapar.
    """
    try:
        import pandas as pd
        
        # Predictor'ı al (checkpoint'ten yüklemeyi dener)
        predictor = get_energy_predictor(
            location=request.location,
            include_weather=request.include_weather
        )
        
        # Eğer model eğitilmişse, direkt tahmin yap
        if predictor.is_trained:
            try:
                # Tahmin yap (last_data gerekli, yoksa request'ten al)
                if predictor.last_data is None or len(predictor.last_data) == 0:
                    # Request'ten veri al ve son 200 satırı kullan
                    if request.data and len(request.data) > 0:
                        df = pd.DataFrame(request.data)
                        df = predictor.loader.preprocess_building_data(df)
                        df_features = predictor.feature_engineer.fit_transform(df)
                        predictor.last_data = df_features.tail(200)
                
                forecast = predictor.predict(future_hours=request.future_hours)
                
                # Sonuçları formatla
                predictions = []
                for _, row in forecast.iterrows():
                    predictions.append({
                        "datetime": row[predictor.date_column].isoformat(),
                        "predicted_power": float(row["predicted_power"])
                    })
                
                return ForecastResponse(
                    success=True,
                    predictions=predictions,
                    weather_features=request.include_weather
                )
            except Exception as e:
                print(f"[WARNING] Prediction with trained model failed: {e}, falling back to training")
                # Fall through to training
        
        # Model yoksa veya tahmin başarısız olduysa eğit
        if request.data is None or len(request.data) == 0:
            return ForecastResponse(
                success=False,
                predictions=None,
                weather_features=request.include_weather,
                error="Model eğitilmiş değil ve eğitim için veri gerekli"
            )
        
        # Veriyi DataFrame'e çevir
        df = pd.DataFrame(request.data)
        
        if len(df) < 100:
            return ForecastResponse(
                success=False,
                predictions=None,
                weather_features=request.include_weather,
                error="En az 100 veri noktası gerekli (model eğitimi için)"
            )
        
        # Modeli eğit
        predictor.train(
            df,
            val_ratio=0.15,
            verbose=False
        )
        
        # Tahmin yap
        forecast = predictor.predict(future_hours=request.future_hours)
        
        # Sonuçları formatla
        predictions = []
        for _, row in forecast.iterrows():
            predictions.append({
                "datetime": row[predictor.date_column].isoformat(),
                "predicted_power": float(row["predicted_power"])
            })
        
        return ForecastResponse(
            success=True,
            predictions=predictions,
            weather_features=request.include_weather
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ForecastResponse(
            success=False,
            predictions=None,
            weather_features=request.include_weather,
            error=str(e)
        )


# ============================================================================
# AI INSIGHTS ENDPOINTS
# ============================================================================

class MLInsightRequest(BaseModel):
    """ML AI öneri isteği"""
    tab_type: str = Field(..., description="Sekme tipi: net_zero, benchmark, anomaly, forecast, overview")
    data: Dict = Field(..., description="Sekmeye özel veri")


class MLInsightResponse(BaseModel):
    """ML AI öneri yanıtı"""
    success: bool
    insights: Optional[str] = None
    error: Optional[str] = None


@router.post("/ai-insights", response_model=MLInsightResponse)
async def get_ml_insights(request: MLInsightRequest):
    """
    ML Dashboard sekmeleri için AI önerileri
    
    Her sekme için özel AI analizi ve öneriler sunar.
    Timeout koruması ile blocking işlemleri önler.
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    try:
        advisor = get_ml_advisor()
        if advisor is None:
            return MLInsightResponse(
                success=False,
                error="AI servisi kullanılamıyor (LM Studio bağlantısı gerekli)"
            )
        
        tab_type = request.tab_type.lower()
        data = request.data
        
        # AI çağrısını thread pool'da çalıştır (blocking önlemek için)
        def generate_insights_sync():
            if tab_type == 'net_zero':
                return advisor.generate_net_zero_recommendations(
                    company_name=data.get('company_name', 'Şirket'),
                    current_emissions={
                        'scope1': data.get('scope1_emissions', 0),
                        'scope2': data.get('scope2_emissions', 0),
                        'scope3': data.get('scope3_emissions', 0)
                    },
                    target_year=data.get('target_year', 2030),
                    base_year=data.get('base_year', 2024),
                    reduction_target=data.get('reduction_target', 0),
                    milestones=data.get('milestones'),
                    investment=data.get('investment')
                )
            elif tab_type == 'benchmark':
                return advisor.generate_benchmark_insights(
                    company_name=data.get('company_name', 'Şirket'),
                    sector=data.get('sector', ''),
                    company_metrics=data.get('company_metrics', {}),
                    sector_average=data.get('sector_average', {}),
                    percentile=data.get('percentile', 50)
                )
            elif tab_type == 'anomaly':
                return advisor.generate_anomaly_analysis(
                    anomaly_count=data.get('anomaly_count', 0),
                    anomaly_indices=data.get('anomaly_indices', []),
                    data_summary=data.get('data_summary', {}),
                    anomaly_details=data.get('anomaly_details')
                )
            elif tab_type == 'forecast':
                return advisor.generate_forecast_recommendations(
                    forecast_summary=data.get('forecast_summary', {}),
                    current_consumption=data.get('current_consumption'),
                    location=data.get('location')
                )
            elif tab_type == 'overview':
                return advisor.generate_overview_insights(
                    company_name=data.get('company_name', 'Şirket'),
                    esg_summary=data.get('esg_summary', {}),
                    ml_results=data.get('ml_results')
                )
            else:
                raise ValueError(f"Geçersiz sekme tipi: {tab_type}")
        
        # Thread pool ile async çalıştır (30 saniye timeout)
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            try:
                insights = await asyncio.wait_for(
                    loop.run_in_executor(executor, generate_insights_sync),
                    timeout=30.0  # 30 saniye timeout
                )
                return MLInsightResponse(
                    success=True,
                    insights=insights
                )
            except asyncio.TimeoutError:
                return MLInsightResponse(
                    success=False,
                    error="AI önerileri zaman aşımına uğradı. Lütfen tekrar deneyin."
                )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return MLInsightResponse(
            success=False,
            error=str(e)
        )


@router.post("/clear-cache")
async def clear_cache():
    """
    Tüm ML model cache'lerini temizle
    
    Global model instance'larını ve AI advisor cache'ini sıfırlar.
    Backend donduğunda veya cache sorunlarında kullanılabilir.
    """
    global _benchmarker, _recommender, _anomaly_detector, _energy_predictor, _ml_advisor
    
    try:
        # Model cache'lerini temizle
        _benchmarker = None
        _recommender = None
        _anomaly_detector = None
        _energy_predictor = None
        _ml_advisor = None
        
        # Python cache temizle (opsiyonel - sadece bilgi)
        import gc
        gc.collect()
        
        return {
            "success": True,
            "message": "Tüm cache'ler temizlendi",
            "cleared": {
                "benchmarker": True,
                "recommender": True,
                "anomaly_detector": True,
                "energy_predictor": True,
                "ml_advisor": True
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

