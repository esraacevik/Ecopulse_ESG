"""
ESG Analyzer & OCR API Endpoints - Enhanced Version
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.esg_analyzer import ESGAnalyzer
from app.services.ocr_extractor import OCRExtractor

router = APIRouter(prefix="/analyzer", tags=["ESG Analyzer"])

# Initialize services
esg_analyzer = ESGAnalyzer()
ocr_extractor = OCRExtractor()


class TextAnalysisRequest(BaseModel):
    text: str


# Gelişmiş response modelleri
class ScopeDetail(BaseModel):
    detected: bool
    score: float
    primary_matches: int
    secondary_matches: int
    confidence: str


class ESGCategoryDetail(BaseModel):
    percentage: float
    raw_score: int
    top_keywords: List[str]


class RiskComponents(BaseModel):
    scope_coverage: int
    emission_data: int
    esg_balance: int
    sentiment: int
    transparency: int


class RiskScoreDetail(BaseModel):
    total: int
    level: str
    color: str
    components: RiskComponents


class SentimentDetail(BaseModel):
    score: int
    label: str
    positive_indicators: int
    negative_indicators: int
    high_risk_count: int
    medium_risk_count: int


class TargetsDetail(BaseModel):
    net_zero: Optional[int] = None
    reduction_targets: List[int] = []
    certifications: List[str] = []


class ConfidenceDetail(BaseModel):
    score: int
    level: str


class RecommendationDetail(BaseModel):
    priority: str
    category: str
    title: str
    description: str
    impact: str


class ESGAnalysisResponseV2(BaseModel):
    success: bool
    scope_detection: Dict[str, ScopeDetail]
    emission_values: List[Dict[str, Any]]
    esg_classification: Dict[str, ESGCategoryDetail]
    risk_score: RiskScoreDetail
    sentiment: SentimentDetail
    targets: TargetsDetail
    confidence: ConfidenceDetail
    summary: str
    recommendations: List[RecommendationDetail]
    error: Optional[str] = None


# Eski basit response model (eski frontend uyumluluğu için)
class ESGAnalysisResponseSimple(BaseModel):
    success: bool
    scope_detection: Dict[str, bool]
    emission_values: List[Dict]
    esg_classification: Dict[str, float]
    risk_score: int
    summary: str
    recommendations: List[str]
    # Yeni alanlar (opsiyonel)
    sentiment: Optional[Dict] = None
    targets: Optional[Dict] = None
    confidence: Optional[Dict] = None
    risk_details: Optional[Dict] = None
    error: Optional[str] = None


class OCRResponse(BaseModel):
    success: bool
    raw_text: str
    extracted_data: List[Dict]
    confidence: float
    error: Optional[str] = None


class InvoiceDataResponse(BaseModel):
    success: bool
    electricity_kwh: float
    natural_gas_m3: float
    water_litre: float
    period: str
    amount_tl: float
    raw_values: List[Dict]
    error: Optional[str] = None


def convert_to_simple_response(results: Dict) -> Dict:
    """
    Gelişmiş ESGAnalyzer sonuçlarını basit frontend formatına dönüştür
    """
    # Scope detection - sadece bool
    simple_scope = {}
    for scope_key, scope_data in results.get("scope_detection", {}).items():
        if isinstance(scope_data, dict):
            simple_scope[scope_key] = scope_data.get("detected", False)
        else:
            simple_scope[scope_key] = bool(scope_data)
    
    # ESG classification - sadece yüzde
    simple_esg = {}
    for cat, cat_data in results.get("esg_classification", {}).items():
        if isinstance(cat_data, dict):
            simple_esg[cat] = cat_data.get("percentage", 0)
        else:
            simple_esg[cat] = float(cat_data)
    
    # Risk score - sadece int
    risk_data = results.get("risk_score", 0)
    if isinstance(risk_data, dict):
        simple_risk = risk_data.get("total", 0)
    else:
        simple_risk = int(risk_data)
    
    # Recommendations - sadece string listesi
    simple_recs = []
    for rec in results.get("recommendations", []):
        if isinstance(rec, dict):
            simple_recs.append(f"[{rec.get('priority', 'medium').upper()}] {rec.get('title', '')}: {rec.get('description', '')}")
        else:
            simple_recs.append(str(rec))
    
    return {
        "scope_detection": simple_scope,
        "emission_values": results.get("emission_values", []),
        "esg_classification": simple_esg,
        "risk_score": simple_risk,
        "summary": results.get("summary", ""),
        "recommendations": simple_recs,
        # Yeni detayları da ekle
        "sentiment": results.get("sentiment"),
        "targets": results.get("targets"),
        "confidence": results.get("confidence"),
        "risk_details": risk_data if isinstance(risk_data, dict) else None
    }


@router.post("/text", response_model=ESGAnalysisResponseSimple)
async def analyze_text(request: TextAnalysisRequest):
    """
    Gelişmiş metin analizi - ESG içeriğini analiz et
    
    Girdi olarak metin alır ve şunları döndürür:
    - Scope tespiti (1, 2, 3) - güven skoruyla
    - Emisyon değerleri - kategorili
    - ESG sınıflandırması (E/S/G oranları) - detaylı
    - Risk skoru (0-100) - bileşenlerle
    - Sentiment analizi
    - Hedefler ve taahhütler
    - Özet ve öneriler
    """
    try:
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Metin çok kısa veya boş")
        
        results = esg_analyzer.analyze_text(request.text)
        simple = convert_to_simple_response(results)
        
        return ESGAnalysisResponseSimple(
            success=True,
            scope_detection=simple["scope_detection"],
            emission_values=simple["emission_values"],
            esg_classification=simple["esg_classification"],
            risk_score=simple["risk_score"],
            summary=simple["summary"],
            recommendations=simple["recommendations"],
            sentiment=simple["sentiment"],
            targets=simple["targets"],
            confidence=simple["confidence"],
            risk_details=simple["risk_details"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text/detailed")
async def analyze_text_detailed(request: TextAnalysisRequest):
    """
    Detaylı metin analizi - Tüm analiz verilerini döndürür
    """
    try:
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Metin çok kısa veya boş")
        
        results = esg_analyzer.analyze_text(request.text)
        results["success"] = True
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pdf", response_model=ESGAnalysisResponseSimple)
async def analyze_pdf(file: UploadFile = File(...)):
    """
    PDF analizi - ESG raporunu analiz et
    
    PDF dosyası yükler ve içeriğini analiz eder.
    Metin tabanlı PDF'ler için en iyi sonucu verir.
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Sadece PDF dosyaları kabul edilir")
        
        contents = await file.read()
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Dosya boş")
        
        results = esg_analyzer.analyze_pdf_bytes(contents)
        
        if "error" in results and results.get("error"):
            simple = convert_to_simple_response(results)
            return ESGAnalysisResponseSimple(
                success=False,
                scope_detection=simple["scope_detection"],
                emission_values=simple["emission_values"],
                esg_classification=simple["esg_classification"],
                risk_score=simple["risk_score"],
                summary=simple["summary"],
                recommendations=simple["recommendations"],
                error=results["error"]
            )
        
        simple = convert_to_simple_response(results)
        
        return ESGAnalysisResponseSimple(
            success=True,
            scope_detection=simple["scope_detection"],
            emission_values=simple["emission_values"],
            esg_classification=simple["esg_classification"],
            risk_score=simple["risk_score"],
            summary=simple["summary"],
            recommendations=simple["recommendations"],
            sentiment=simple["sentiment"],
            targets=simple["targets"],
            confidence=simple["confidence"],
            risk_details=simple["risk_details"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr/image", response_model=OCRResponse)
async def ocr_image(file: UploadFile = File(...)):
    """
    Görüntü OCR - Fatura/belge görüntüsünden metin çıkar
    
    Desteklenen formatlar: PNG, JPG, JPEG, TIFF, BMP
    """
    try:
        valid_extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        ext = '.' + file.filename.lower().split('.')[-1]
        
        if ext not in valid_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Desteklenmeyen format. Kabul edilenler: {', '.join(valid_extensions)}"
            )
        
        contents = await file.read()
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Dosya boş")
        
        results = ocr_extractor.extract_from_image_bytes(contents, file.filename)
        
        return OCRResponse(
            success=results["success"],
            raw_text=results["raw_text"],
            extracted_data=results["extracted_data"],
            confidence=results["confidence"],
            error=results.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr/pdf", response_model=OCRResponse)
async def ocr_pdf(file: UploadFile = File(...)):
    """
    PDF OCR - Taranmış PDF'den metin çıkar
    
    Hem metin tabanlı hem de taranmış (image-based) PDF'leri işleyebilir.
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Sadece PDF dosyaları kabul edilir")
        
        contents = await file.read()
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Dosya boş")
        
        results = ocr_extractor.extract_from_pdf_bytes(contents)
        
        return OCRResponse(
            success=results["success"],
            raw_text=results["raw_text"],
            extracted_data=results["extracted_data"],
            confidence=results.get("confidence", 0),
            error=results.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoice", response_model=InvoiceDataResponse)
async def extract_invoice(file: UploadFile = File(...)):
    """
    Fatura verisi çıkarma - Elektrik/doğalgaz faturasından otomatik veri çıkar
    
    Fatura görüntüsünden şunları otomatik tespit eder:
    - Elektrik tüketimi (kWh)
    - Doğalgaz tüketimi (m³)
    - Fatura dönemi
    - Toplam tutar
    """
    try:
        contents = await file.read()
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Dosya boş")
        
        filename_lower = file.filename.lower()
        
        if filename_lower.endswith('.pdf'):
            ocr_result = ocr_extractor.extract_from_pdf_bytes(contents)
        elif any(filename_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']):
            ocr_result = ocr_extractor.extract_from_image_bytes(contents, file.filename)
        else:
            raise HTTPException(status_code=400, detail="Desteklenmeyen dosya formatı")
        
        if not ocr_result["success"]:
            return InvoiceDataResponse(
                success=False,
                electricity_kwh=0,
                natural_gas_m3=0,
                water_litre=0,
                period="",
                amount_tl=0,
                raw_values=[],
                error=ocr_result.get("error", "OCR başarısız")
            )
        
        invoice_data = ocr_extractor.extract_invoice_data(ocr_result["raw_text"])
        
        return InvoiceDataResponse(
            success=True,
            electricity_kwh=invoice_data["electricity_kwh"],
            natural_gas_m3=invoice_data["natural_gas_m3"],
            water_litre=invoice_data["water_litre"],
            period=invoice_data["period"],
            amount_tl=invoice_data["amount_tl"],
            raw_values=invoice_data["raw_values"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def analyzer_status():
    """
    Analyzer servisi durumu
    """
    return {
        "esg_analyzer": "active",
        "esg_analyzer_version": "2.0",
        "features": {
            "scope_detection": True,
            "emission_extraction": True,
            "esg_classification": True,
            "risk_scoring": True,
            "sentiment_analysis": True,
            "target_extraction": True
        },
        "ocr_available": ocr_extractor.tesseract_available,
        "huggingface_api": esg_analyzer.use_api,
        "supported_formats": {
            "pdf": True,
            "images": ocr_extractor.supported_formats
        }
    }
