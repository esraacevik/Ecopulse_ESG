"""
Emission Calculation API Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir.parent))

from app.models.schemas import EmissionInput, EmissionCalculationResponse, EmissionResult
from app.services.hybrid_calculator import HybridEmissionCalculator

router = APIRouter()

@router.post("/emission/calculate", response_model=EmissionCalculationResponse)
async def calculate_emission(input_data: EmissionInput):
    """
    Calculate carbon emissions from energy consumption
    
    Uses hybrid calculator (Climatiq → EPA → Manual fallback)
    """
    try:
        calculator = HybridEmissionCalculator()
        results = []
        
        # Calculate electricity emissions
        if input_data.electricity_kwh > 0:
            elec_result = calculator.calculate_emission(
                category="electricity",
                amount=input_data.electricity_kwh,
                unit="kWh",
                region=input_data.region
            )
            
            if elec_result["co2_kg"] > 0:
                results.append(EmissionResult(
                    activity_name="Electricity consumption",
                    amount=input_data.electricity_kwh,
                    unit="kWh",
                    co2e_kg=elec_result["co2_kg"],
                    co2e_ton=elec_result["co2_kg"] / 1000,
                    scope=elec_result["scope"],
                    category="Enerji",
                    region=input_data.region,
                    source=elec_result["source"],
                    confidence=elec_result["confidence"]
                ))
        
        # Calculate district heating emissions (Scope 2)
        if input_data.heating_kwh > 0:
            heating_result = calculator.calculate_emission(
                category="heating",
                amount=input_data.heating_kwh,
                unit="kWh",
                region=input_data.region
            )
            
            if heating_result["co2_kg"] > 0:
                results.append(EmissionResult(
                    activity_name="District heating consumption",
                    amount=input_data.heating_kwh,
                    unit="kWh",
                    co2e_kg=heating_result["co2_kg"],
                    co2e_ton=heating_result["co2_kg"] / 1000,
                    scope="Scope 2",
                    category="Enerji",
                    region=input_data.region,
                    source=heating_result["source"],
                    confidence=heating_result["confidence"]
                ))
        
        # Calculate district cooling emissions (Scope 2)
        if input_data.cooling_kwh > 0:
            cooling_result = calculator.calculate_emission(
                category="cooling",
                amount=input_data.cooling_kwh,
                unit="kWh",
                region=input_data.region
            )
            
            if cooling_result["co2_kg"] > 0:
                results.append(EmissionResult(
                    activity_name="District cooling consumption",
                    amount=input_data.cooling_kwh,
                    unit="kWh",
                    co2e_kg=cooling_result["co2_kg"],
                    co2e_ton=cooling_result["co2_kg"] / 1000,
                    scope="Scope 2",
                    category="Enerji",
                    region=input_data.region,
                    source=cooling_result["source"],
                    confidence=cooling_result["confidence"]
                ))
        
        # Calculate natural gas emissions
        if input_data.natural_gas_m3 > 0:
            gas_result = calculator.calculate_emission(
                category="natural_gas",
                amount=input_data.natural_gas_m3,
                unit="m³",
                region=input_data.region
            )
            
            if gas_result["co2_kg"] > 0:
                results.append(EmissionResult(
                    activity_name="Natural gas consumption",
                    amount=input_data.natural_gas_m3,
                    unit="m³",
                    co2e_kg=gas_result["co2_kg"],
                    co2e_ton=gas_result["co2_kg"] / 1000,
                    scope=gas_result["scope"],
                    category="Enerji",
                    region=input_data.region,
                    source=gas_result["source"],
                    confidence=gas_result["confidence"]
                ))
        
        # Calculate diesel emissions
        if input_data.diesel_litre > 0:
            diesel_result = calculator.calculate_emission(
                category="diesel",
                amount=input_data.diesel_litre,
                unit="litre",
                region=input_data.region
            )
            
            if diesel_result["co2_kg"] > 0:
                results.append(EmissionResult(
                    activity_name="Diesel consumption",
                    amount=input_data.diesel_litre,
                    unit="litre",
                    co2e_kg=diesel_result["co2_kg"],
                    co2e_ton=diesel_result["co2_kg"] / 1000,
                    scope=diesel_result["scope"],
                    category="Ulaşım",
                    region=input_data.region,
                    source=diesel_result["source"],
                    confidence=diesel_result["confidence"]
                ))
        
        # Calculate petrol emissions
        if input_data.petrol_litre > 0:
            petrol_result = calculator.calculate_emission(
                category="petrol",
                amount=input_data.petrol_litre,
                unit="litre",
                region=input_data.region
            )
            
            if petrol_result["co2_kg"] > 0:
                results.append(EmissionResult(
                    activity_name="Petrol consumption",
                    amount=input_data.petrol_litre,
                    unit="litre",
                    co2e_kg=petrol_result["co2_kg"],
                    co2e_ton=petrol_result["co2_kg"] / 1000,
                    scope=petrol_result["scope"],
                    category="Ulaşım",
                    region=input_data.region,
                    source=petrol_result["source"],
                    confidence=petrol_result["confidence"]
                ))
        
        # Calculate LPG emissions
        if input_data.lpg_litre > 0:
            lpg_result = calculator.calculate_emission(
                category="lpg",
                amount=input_data.lpg_litre,
                unit="litre",
                region=input_data.region
            )
            
            if lpg_result["co2_kg"] > 0:
                results.append(EmissionResult(
                    activity_name="LPG consumption",
                    amount=input_data.lpg_litre,
                    unit="litre",
                    co2e_kg=lpg_result["co2_kg"],
                    co2e_ton=lpg_result["co2_kg"] / 1000,
                    scope=lpg_result["scope"],
                    category="Enerji",
                    region=input_data.region,
                    source=lpg_result["source"],
                    confidence=lpg_result["confidence"]
                ))
        
        # Calculate coal emissions
        if input_data.coal_kg > 0:
            coal_result = calculator.calculate_emission(
                category="coal",
                amount=input_data.coal_kg,
                unit="kg",
                region=input_data.region
            )
            
            if coal_result["co2_kg"] > 0:
                results.append(EmissionResult(
                    activity_name="Coal consumption",
                    amount=input_data.coal_kg,
                    unit="kg",
                    co2e_kg=coal_result["co2_kg"],
                    co2e_ton=coal_result["co2_kg"] / 1000,
                    scope=coal_result["scope"],
                    category="Enerji",
                    region=input_data.region,
                    source=coal_result["source"],
                    confidence=coal_result["confidence"]
                ))
        
        # Calculate fuel oil emissions
        if input_data.fuel_oil_litre > 0:
            fuel_oil_result = calculator.calculate_emission(
                category="fuel_oil",
                amount=input_data.fuel_oil_litre,
                unit="litre",
                region=input_data.region
            )
            
            if fuel_oil_result["co2_kg"] > 0:
                results.append(EmissionResult(
                    activity_name="Fuel oil consumption",
                    amount=input_data.fuel_oil_litre,
                    unit="litre",
                    co2e_kg=fuel_oil_result["co2_kg"],
                    co2e_ton=fuel_oil_result["co2_kg"] / 1000,
                    scope="Scope 1",
                    category="Enerji",
                    region=input_data.region,
                    source=fuel_oil_result["source"],
                    confidence=fuel_oil_result["confidence"]
                ))
        
        # Calculate biogas emissions
        if input_data.biogas_kwh > 0:
            biogas_result = calculator.calculate_emission(
                category="biogas",
                amount=input_data.biogas_kwh,
                unit="kWh",
                region=input_data.region
            )
            
            if biogas_result["co2_kg"] > 0:
                results.append(EmissionResult(
                    activity_name="Biogas consumption",
                    amount=input_data.biogas_kwh,
                    unit="kWh",
                    co2e_kg=biogas_result["co2_kg"],
                    co2e_ton=biogas_result["co2_kg"] / 1000,
                    scope="Scope 1",
                    category="Enerji",
                    region=input_data.region,
                    source=biogas_result["source"],
                    confidence=biogas_result["confidence"]
                ))
        
        # Calculate refrigerant leakage emissions
        if input_data.refrigerant_kg > 0:
            refrigerant_result = calculator.calculate_emission(
                category="refrigerant",
                amount=input_data.refrigerant_kg,
                unit="kg",
                region=input_data.region
            )
            
            if refrigerant_result["co2_kg"] > 0:
                results.append(EmissionResult(
                    activity_name="Refrigerant leakage (R-134a)",
                    amount=input_data.refrigerant_kg,
                    unit="kg",
                    co2e_kg=refrigerant_result["co2_kg"],
                    co2e_ton=refrigerant_result["co2_kg"] / 1000,
                    scope="Scope 1",
                    category="Kaçak Gazlar",
                    region=input_data.region,
                    source=refrigerant_result["source"],
                    confidence=refrigerant_result["confidence"]
                ))
        
        # Calculate water emissions (Scope 3 - water supply & treatment)
        if input_data.water_litre > 0:
            water_factor = 0.0003  # kg CO2e per litre (water treatment)
            co2_kg = input_data.water_litre * water_factor
            if co2_kg > 0:
                results.append(EmissionResult(
                    activity_name="Water consumption",
                    amount=input_data.water_litre,
                    unit="litre",
                    co2e_kg=co2_kg,
                    co2e_ton=co2_kg / 1000,
                    scope="Scope 3",
                    category="Su",
                    region=input_data.region,
                    source="Manual",
                    confidence="medium"
                ))
        
        # Calculate waste emissions with waste type support
        if input_data.waste_kg > 0:
            # Waste factors by disposal type
            waste_factors = {
                "landfill": 0.58,      # Landfill emissions
                "recycling": 0.02,     # Recycling (very low)
                "incineration": 0.91   # Incineration
            }
            waste_type = getattr(input_data, 'waste_type', 'landfill')
            waste_factor = waste_factors.get(waste_type, 0.58)
            co2_kg = input_data.waste_kg * waste_factor
            
            waste_labels = {
                "landfill": "Waste disposal (Landfill)",
                "recycling": "Waste disposal (Recycling)",
                "incineration": "Waste disposal (Incineration)"
            }
            
            if co2_kg > 0:
                results.append(EmissionResult(
                    activity_name=waste_labels.get(waste_type, "Waste disposal"),
                    amount=input_data.waste_kg,
                    unit="kg",
                    co2e_kg=co2_kg,
                    co2e_ton=co2_kg / 1000,
                    scope="Scope 3",
                    category="Atık",
                    region=input_data.region,
                    source="Manual",
                    confidence="medium"
                ))
        
        # Calculate vehicle emissions
        if input_data.vehicle_km > 0:
            vehicle_result = None
            source = "Manual"
            confidence = "medium"
            
            # Try Climatiq API first
            try:
                from app.services.climatiq_service import ClimatiqCalculator
                climatiq = ClimatiqCalculator()
                
                if input_data.vehicle_fuel_type == "Dizel":
                    vehicle_result = climatiq.calculate_diesel_vehicle(input_data.vehicle_km, input_data.region)
                elif input_data.vehicle_fuel_type == "Benzin":
                    vehicle_result = climatiq.calculate_petrol_vehicle(input_data.vehicle_km, input_data.region)
                
                if vehicle_result:
                    source = "Climatiq API"
                    confidence = "high"
            except Exception as e:
                print(f"[WARN] Climatiq vehicle calculation failed: {e}")
                vehicle_result = None
            
            # Fallback to manual factors if Climatiq fails
            if vehicle_result:
                co2e_kg = vehicle_result.co2e_kg
                co2e_ton = vehicle_result.co2e_ton
                scope = vehicle_result.scope
            else:
                # Manual emission factors (kg CO2e per km)
                vehicle_factors = {
                    "Dizel": 0.171,  # kg CO2e/km for diesel car
                    "Benzin": 0.192,  # kg CO2e/km for petrol car
                    "Elektrikli": 0.053  # kg CO2e/km for electric car (grid average)
                }
                factor = vehicle_factors.get(input_data.vehicle_fuel_type, 0.171)
                co2e_kg = input_data.vehicle_km * factor
                co2e_ton = co2e_kg / 1000
                scope = "Scope 1"
            
            results.append(EmissionResult(
                activity_name=f"Vehicle travel ({input_data.vehicle_fuel_type})",
                amount=input_data.vehicle_km,
                unit="km",
                co2e_kg=co2e_kg,
                co2e_ton=co2e_ton,
                scope=scope,
                category="Ulaşım",
                region=input_data.region,
                source=source,
                confidence=confidence
            ))
        
        # Calculate flight emissions
        if input_data.flight_km > 0:
            flight_result = None
            source = "Manual"
            confidence = "medium"
            
            # Try Climatiq API first
            try:
                from app.services.climatiq_service import ClimatiqCalculator
                climatiq = ClimatiqCalculator()
                
                if input_data.flight_class == "Ekonomi":
                    flight_result = climatiq.calculate_flight_economy(input_data.flight_km)
                elif input_data.flight_class == "Business":
                    flight_result = climatiq.calculate_flight_business(input_data.flight_km)
                else:  # First Class
                    flight_result = climatiq.calculate_flight_business(input_data.flight_km)
                
                if flight_result:
                    source = "Climatiq API"
                    confidence = "high"
            except Exception as e:
                print(f"[WARN] Climatiq flight calculation failed: {e}")
                flight_result = None
            
            # Fallback to manual factors if Climatiq fails
            if flight_result:
                co2e_kg = flight_result.co2e_kg
                co2e_ton = flight_result.co2e_ton
                scope = flight_result.scope
            else:
                # Manual emission factors (kg CO2e per km)
                flight_factors = {
                    "Ekonomi": 0.255,  # kg CO2e/km for economy class
                    "Business": 0.765,  # kg CO2e/km for business class
                    "First Class": 1.020  # kg CO2e/km for first class
                }
                factor = flight_factors.get(input_data.flight_class, 0.255)
                co2e_kg = input_data.flight_km * factor
                co2e_ton = co2e_kg / 1000
                scope = "Scope 3"
            
            results.append(EmissionResult(
                activity_name=f"Flight travel ({input_data.flight_class})",
                amount=input_data.flight_km,
                unit="km",
                co2e_kg=co2e_kg,
                co2e_ton=co2e_ton,
                scope=scope,
                category="Ulaşım",
                region=input_data.region,
                source=source,
                confidence=confidence
            ))
        
        # ============== NEW SCOPE 3 CALCULATIONS ==============
        
        # Calculate hotel/accommodation emissions
        if input_data.hotel_nights > 0:
            hotel_result = calculator.calculate_emission(
                category="hotel",
                amount=input_data.hotel_nights,
                unit="night",
                region=input_data.region
            )
            co2_kg = hotel_result["co2_kg"] if hotel_result["co2_kg"] > 0 else input_data.hotel_nights * 21.0
            results.append(EmissionResult(
                activity_name="Hotel accommodation",
                amount=input_data.hotel_nights,
                unit="nights",
                co2e_kg=co2_kg,
                co2e_ton=co2_kg / 1000,
                scope="Scope 3",
                category="İş Seyahati",
                region=input_data.region,
                source=hotel_result["source"] if hotel_result["co2_kg"] > 0 else "Manual",
                confidence=hotel_result["confidence"] if hotel_result["co2_kg"] > 0 else "medium"
            ))
        
        # Calculate taxi emissions
        if input_data.taxi_km > 0:
            taxi_result = calculator.calculate_emission(
                category="taxi",
                amount=input_data.taxi_km,
                unit="km",
                region=input_data.region
            )
            co2_kg = taxi_result["co2_kg"] if taxi_result["co2_kg"] > 0 else input_data.taxi_km * 0.21
            results.append(EmissionResult(
                activity_name="Taxi travel",
                amount=input_data.taxi_km,
                unit="km",
                co2e_kg=co2_kg,
                co2e_ton=co2_kg / 1000,
                scope="Scope 3",
                category="İş Seyahati",
                region=input_data.region,
                source=taxi_result["source"] if taxi_result["co2_kg"] > 0 else "Manual",
                confidence=taxi_result["confidence"] if taxi_result["co2_kg"] > 0 else "medium"
            ))
        
        # Calculate train emissions
        if input_data.train_km > 0:
            train_result = calculator.calculate_emission(
                category="train",
                amount=input_data.train_km,
                unit="km",
                region=input_data.region
            )
            co2_kg = train_result["co2_kg"] if train_result["co2_kg"] > 0 else input_data.train_km * 0.041
            results.append(EmissionResult(
                activity_name="Train travel",
                amount=input_data.train_km,
                unit="km",
                co2e_kg=co2_kg,
                co2e_ton=co2_kg / 1000,
                scope="Scope 3",
                category="Ulaşım",
                region=input_data.region,
                source=train_result["source"] if train_result["co2_kg"] > 0 else "Manual",
                confidence=train_result["confidence"] if train_result["co2_kg"] > 0 else "medium"
            ))
        
        # Calculate bus emissions
        if input_data.bus_km > 0:
            bus_result = calculator.calculate_emission(
                category="bus",
                amount=input_data.bus_km,
                unit="km",
                region=input_data.region
            )
            co2_kg = bus_result["co2_kg"] if bus_result["co2_kg"] > 0 else input_data.bus_km * 0.089
            results.append(EmissionResult(
                activity_name="Bus travel",
                amount=input_data.bus_km,
                unit="km",
                co2e_kg=co2_kg,
                co2e_ton=co2_kg / 1000,
                scope="Scope 3",
                category="Ulaşım",
                region=input_data.region,
                source=bus_result["source"] if bus_result["co2_kg"] > 0 else "Manual",
                confidence=bus_result["confidence"] if bus_result["co2_kg"] > 0 else "medium"
            ))
        
        # Calculate metro/subway emissions
        if input_data.metro_km > 0:
            metro_result = calculator.calculate_emission(
                category="metro",
                amount=input_data.metro_km,
                unit="km",
                region=input_data.region
            )
            co2_kg = metro_result["co2_kg"] if metro_result["co2_kg"] > 0 else input_data.metro_km * 0.033
            results.append(EmissionResult(
                activity_name="Metro/Subway travel",
                amount=input_data.metro_km,
                unit="km",
                co2e_kg=co2_kg,
                co2e_ton=co2_kg / 1000,
                scope="Scope 3",
                category="Ulaşım",
                region=input_data.region,
                source=metro_result["source"] if metro_result["co2_kg"] > 0 else "Manual",
                confidence=metro_result["confidence"] if metro_result["co2_kg"] > 0 else "medium"
            ))
        
        # Calculate freight emissions
        if input_data.freight_ton_km > 0:
            freight_result = calculator.calculate_emission(
                category="freight",
                amount=input_data.freight_ton_km,
                unit="ton-km",
                region=input_data.region
            )
            co2_kg = freight_result["co2_kg"] if freight_result["co2_kg"] > 0 else input_data.freight_ton_km * 0.062
            results.append(EmissionResult(
                activity_name="Freight transport",
                amount=input_data.freight_ton_km,
                unit="ton-km",
                co2e_kg=co2_kg,
                co2e_ton=co2_kg / 1000,
                scope="Scope 3",
                category="Tedarik Zinciri",
                region=input_data.region,
                source=freight_result["source"] if freight_result["co2_kg"] > 0 else "Manual",
                confidence=freight_result["confidence"] if freight_result["co2_kg"] > 0 else "medium"
            ))
        
        # Calculate paper consumption emissions
        if input_data.paper_kg > 0:
            paper_result = calculator.calculate_emission(
                category="paper",
                amount=input_data.paper_kg,
                unit="kg",
                region=input_data.region
            )
            co2_kg = paper_result["co2_kg"] if paper_result["co2_kg"] > 0 else input_data.paper_kg * 0.94
            results.append(EmissionResult(
                activity_name="Paper consumption",
                amount=input_data.paper_kg,
                unit="kg",
                co2e_kg=co2_kg,
                co2e_ton=co2_kg / 1000,
                scope="Scope 3",
                category="Satın Alımlar",
                region=input_data.region,
                source=paper_result["source"] if paper_result["co2_kg"] > 0 else "Manual",
                confidence=paper_result["confidence"] if paper_result["co2_kg"] > 0 else "medium"
            ))
        
        if not results:
            raise HTTPException(
                status_code=400,
                detail="No valid emissions calculated. Please provide at least one consumption value > 0"
            )
        
        # Calculate totals
        total_co2e_kg = sum(r.co2e_kg for r in results)
        total_co2e_ton = total_co2e_kg / 1000
        
        # Scope summary
        scope_summary = {}
        for r in results:
            scope_summary[r.scope] = scope_summary.get(r.scope, 0) + r.co2e_ton
        
        return EmissionCalculationResponse(
            results=results,
            total_co2e_kg=total_co2e_kg,
            total_co2e_ton=total_co2e_ton,
            scope_summary=scope_summary
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emission/sources")
async def get_emission_sources():
    """Get available emission data sources"""
    try:
        calculator = HybridEmissionCalculator()
        sources = calculator.get_source_info()
        return sources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

