"""
File Upload API - CSV/Excel parsing for emission data
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import io
import json

router = APIRouter()

class ExtractedData(BaseModel):
    """Extracted emission data from file"""
    rows: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    file_type: str
    filename: str

class UploadResponse(BaseModel):
    """Upload response"""
    success: bool
    message: str
    data: Optional[ExtractedData] = None
    error: Optional[str] = None

@router.post("/upload/parse", response_model=UploadResponse)
async def parse_upload(file: UploadFile = File(...)):
    """
    Parse uploaded file (CSV/Excel) and extract emission data
    """
    try:
        # Check file extension
        filename = file.filename or "unknown"
        file_ext = filename.split('.')[-1].lower()
        
        if file_ext not in ['csv', 'xlsx', 'xls']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Use CSV or Excel files."
            )
        
        # Read file content
        content = await file.read()
        
        # Parse based on file type
        if file_ext == 'csv':
            df = pd.read_csv(io.BytesIO(content))
            file_type = 'csv'
        else:
            df = pd.read_excel(io.BytesIO(content))
            file_type = 'excel'
        
        # Convert to list of dicts
        rows = df.to_dict(orient='records')
        columns = list(df.columns)
        
        # Clean NaN values
        for row in rows:
            for key, value in row.items():
                if pd.isna(value):
                    row[key] = None
        
        extracted_data = ExtractedData(
            rows=rows,
            columns=columns,
            row_count=len(rows),
            file_type=file_type,
            filename=filename
        )
        
        return UploadResponse(
            success=True,
            message=f"Successfully parsed {len(rows)} rows from {filename}",
            data=extracted_data
        )
        
    except pd.errors.EmptyDataError:
        return UploadResponse(
            success=False,
            message="File is empty",
            error="The uploaded file contains no data"
        )
    except Exception as e:
        return UploadResponse(
            success=False,
            message="Failed to parse file",
            error=str(e)
        )

@router.post("/upload/extract-emissions")
async def extract_emissions(file: UploadFile = File(...)):
    """
    Parse file and attempt to extract emission-related data
    """
    try:
        filename = file.filename or "unknown"
        file_ext = filename.split('.')[-1].lower()
        
        if file_ext not in ['csv', 'xlsx', 'xls']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}"
            )
        
        content = await file.read()
        
        if file_ext == 'csv':
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        # Try to identify emission-related columns
        emission_keywords = [
            'electricity', 'elektrik', 'kwh', 'kw',
            'gas', 'gaz', 'm3', 'm³',
            'diesel', 'dizel', 'litre', 'liter',
            'petrol', 'benzin', 'fuel', 'yakıt',
            'co2', 'carbon', 'karbon', 'emission', 'emisyon',
            'scope', 'kapsam',
            'vehicle', 'araç', 'km', 'distance', 'mesafe',
            'flight', 'uçak', 'waste', 'atık', 'water', 'su'
        ]
        
        # Find matching columns
        matched_columns = []
        for col in df.columns:
            col_lower = str(col).lower()
            for keyword in emission_keywords:
                if keyword in col_lower:
                    matched_columns.append(col)
                    break
        
        # Extract emission data structure
        extracted_emissions = []
        
        for _, row in df.iterrows():
            emission_entry = {}
            
            for col in df.columns:
                col_lower = str(col).lower()
                value = row[col]
                
                # Skip NaN values
                if pd.isna(value):
                    continue
                
                # Map to emission fields
                if any(k in col_lower for k in ['electricity', 'elektrik', 'kwh']):
                    emission_entry['electricity_kwh'] = float(value) if isinstance(value, (int, float)) else 0
                elif any(k in col_lower for k in ['gas', 'gaz', 'm3', 'm³']):
                    emission_entry['natural_gas_m3'] = float(value) if isinstance(value, (int, float)) else 0
                elif any(k in col_lower for k in ['diesel', 'dizel']):
                    emission_entry['diesel_litre'] = float(value) if isinstance(value, (int, float)) else 0
                elif any(k in col_lower for k in ['petrol', 'benzin']):
                    emission_entry['petrol_litre'] = float(value) if isinstance(value, (int, float)) else 0
                elif any(k in col_lower for k in ['lpg']):
                    emission_entry['lpg_litre'] = float(value) if isinstance(value, (int, float)) else 0
                elif any(k in col_lower for k in ['coal', 'kömür']):
                    emission_entry['coal_kg'] = float(value) if isinstance(value, (int, float)) else 0
                elif any(k in col_lower for k in ['region', 'bölge']):
                    emission_entry['region'] = str(value)
                elif any(k in col_lower for k in ['period', 'dönem']):
                    emission_entry['period'] = str(value)
            
            if emission_entry:
                extracted_emissions.append(emission_entry)
        
        return {
            "success": True,
            "filename": filename,
            "total_rows": len(df),
            "matched_columns": matched_columns,
            "extracted_emissions": extracted_emissions[:50],  # Limit to 50 rows
            "message": f"Found {len(matched_columns)} emission-related columns"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

