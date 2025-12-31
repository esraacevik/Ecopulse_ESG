"""
Pydantic Schemas for API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# Emission Schemas
class EmissionInput(BaseModel):
    """Emission calculation input"""
    category: str = Field("Enerji", description="Activity category")
    # Scope 1 - Direct Emissions
    natural_gas_m3: float = Field(0.0, description="Natural gas consumption in m³")
    diesel_litre: float = Field(0.0, description="Diesel consumption in litres")
    petrol_litre: float = Field(0.0, description="Petrol consumption in litres")
    lpg_litre: float = Field(0.0, description="LPG consumption in litres")
    coal_kg: float = Field(0.0, description="Coal consumption in kg")
    fuel_oil_litre: float = Field(0.0, description="Fuel oil consumption in litres")
    biogas_kwh: float = Field(0.0, description="Biogas consumption in kWh")
    refrigerant_kg: float = Field(0.0, description="Refrigerant leakage in kg (R-134a, R-410a)")
    vehicle_km: float = Field(0.0, description="Company vehicle distance in km")
    vehicle_fuel_type: str = Field("Dizel", description="Vehicle fuel type: Dizel, Benzin, Elektrikli")
    # Scope 2 - Indirect Energy
    electricity_kwh: float = Field(0.0, description="Electricity consumption in kWh")
    heating_kwh: float = Field(0.0, description="District heating consumption in kWh")
    cooling_kwh: float = Field(0.0, description="District cooling consumption in kWh")
    # Scope 3 - Value Chain
    water_litre: float = Field(0.0, description="Water consumption in litres")
    waste_kg: float = Field(0.0, description="Waste in kg")
    waste_type: str = Field("landfill", description="Waste disposal: landfill, recycling, incineration")
    flight_km: float = Field(0.0, description="Flight distance in km")
    flight_class: str = Field("Ekonomi", description="Flight class: Ekonomi, Business, First Class")
    hotel_nights: float = Field(0.0, description="Hotel nights for business travel")
    taxi_km: float = Field(0.0, description="Taxi travel distance in km")
    train_km: float = Field(0.0, description="Train travel distance in km")
    bus_km: float = Field(0.0, description="Bus travel distance in km")
    metro_km: float = Field(0.0, description="Metro/subway travel distance in km")
    freight_ton_km: float = Field(0.0, description="Freight transport in ton-km")
    paper_kg: float = Field(0.0, description="Purchased paper in kg")
    # Settings
    region: str = Field("TR", description="Region code")
    period: str = Field("Monthly", description="Time period")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "Enerji",
                "electricity_kwh": 18450,
                "natural_gas_m3": 500,
                "region": "TR",
                "period": "Aylık"
            }
        }

class EmissionResult(BaseModel):
    """Emission calculation result"""
    activity_name: str
    amount: float
    unit: str
    co2e_kg: float
    co2e_ton: float
    scope: str
    category: str
    region: str
    source: str
    confidence: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "activity_name": "Electricity consumption",
                "amount": 18450,
                "unit": "kWh",
                "co2e_kg": 8302.5,
                "co2e_ton": 8.3,
                "scope": "Scope 2",
                "category": "Enerji",
                "region": "TR",
                "source": "Climatiq API",
                "confidence": "high"
            }
        }

class EmissionCalculationResponse(BaseModel):
    """Emission calculation response"""
    results: List[EmissionResult]
    total_co2e_kg: float
    total_co2e_ton: float
    scope_summary: Dict[str, float]
    timestamp: datetime = Field(default_factory=datetime.now)

# Report Schemas
class ReportGenerateRequest(BaseModel):
    """Report generation request"""
    results: List[EmissionResult]
    company_name: str = "Örnek Şirket A.Ş."
    period: str = "2024 Q1"
    filename: Optional[str] = None

class ReportGenerateResponse(BaseModel):
    """Report generation response"""
    success: bool
    filename: str
    file_path: str
    message: str

class ReportProgressMessage(BaseModel):
    """Report generation progress message (for streaming)"""
    type: str  # "progress" | "complete" | "error"
    message: Optional[str] = None
    step: Optional[str] = None  # "cover", "executive_summary", "charts", etc.
    percentage: Optional[int] = None
    filename: Optional[str] = None
    file_path: Optional[str] = None

class ReportInfo(BaseModel):
    """Report metadata information"""
    filename: str
    company_name: str
    period: str
    created_at: str
    file_size: int
    file_path: str

class ReportListResponse(BaseModel):
    """Report list response"""
    success: bool
    reports: List[ReportInfo]
    total_count: int

class ReportDeleteResponse(BaseModel):
    """Report delete response"""
    success: bool
    message: str
    filename: Optional[str] = None

# AI Schemas
class AIChatRequest(BaseModel):
    """AI chat request"""
    message: str
    context: Optional[Dict] = None

class AIChatResponse(BaseModel):
    """AI chat response"""
    response: str
    sources: Optional[List[str]] = None

