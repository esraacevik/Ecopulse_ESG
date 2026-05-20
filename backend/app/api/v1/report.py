"""
Report Generation API Endpoints
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import sys
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import AsyncGenerator

# Add project root to path
# __file__ = backend/app/api/v1/report.py -> project root = backend_dir.parent
backend_dir = Path(__file__).parent.parent.parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from app.models.schemas import (
    ReportGenerateRequest, 
    ReportGenerateResponse, 
    ReportProgressMessage,
    ReportInfo,
    ReportListResponse,
    ReportDeleteResponse,
    EmissionResult
)
from app.services.report_generator import ESG_Report_Generator
from app.services.report_generator_fixed import ESG_Report_Generator_Fixed

router = APIRouter()

@router.post("/report/generate", response_model=ReportGenerateResponse)
async def generate_report(request: ReportGenerateRequest):
    """
    Generate ESG PDF report
    """
    try:
        # Convert Pydantic models to EmissionResult dataclass
        from app.services.climatiq_service import EmissionResult as ER_Dataclass
        
        emission_results = []
        for r in request.results:
            emission_results.append(ER_Dataclass(
                activity_name=r.activity_name,
                amount=r.amount,
                unit=r.unit,
                co2e_kg=r.co2e_kg,
                co2e_ton=r.co2e_ton,
                scope=r.scope,
                category=r.category,
                region=r.region,
                source=r.source,
                year=2024
            ))
        
        # Generate report
        generator = ESG_Report_Generator(
            company_name=request.company_name,
            reporting_period=request.period
        )
        
        filename = request.filename or f"esg_report_{request.company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        # Calculate scope summary
        scope_summary = {}
        for r in emission_results:
            scope_summary[r.scope] = scope_summary.get(r.scope, 0) + r.co2e_ton
        
        generator.generate_report(emission_results, scope_summary, filepath)
        
        return ReportGenerateResponse(
            success=True,
            filename=filename,
            file_path=filepath,
            message="Report generated successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report/generate-stream")
async def generate_report_stream(request: ReportGenerateRequest):
    """
    Generate ESG PDF report with Server-Sent Events (SSE) streaming
    Uses the enhanced report_generator_fixed.py
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Convert Pydantic models to EmissionResult dataclass
            from app.services.climatiq_service import EmissionResult as ER_Dataclass
            
            emission_results = []
            for r in request.results:
                emission_results.append(ER_Dataclass(
                    activity_name=r.activity_name,
                    amount=r.amount,
                    unit=r.unit,
                    co2e_kg=r.co2e_kg,
                    co2e_ton=r.co2e_ton,
                    scope=r.scope,
                    category=r.category,
                    region=r.region,
                    source=r.source,
                    year=2024
                ))
            
            # Calculate scope summary
            scope_summary = {}
            for r in emission_results:
                scope_summary[r.scope] = scope_summary.get(r.scope, 0) + r.co2e_ton
            
            # Generate filename (safe - no Turkish characters)
            def safe_filename(text: str) -> str:
                """Convert text to safe filename (no special chars)"""
                import unicodedata
                import re
                # Normalize unicode
                text = unicodedata.normalize('NFKD', text)
                # Remove special chars, keep only alphanumeric and spaces
                text = re.sub(r'[^\w\s-]', '', text)
                # Replace spaces with underscores
                text = re.sub(r'[-\s]+', '_', text)
                return text
            
            if request.filename:
                filename = safe_filename(request.filename)
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
            else:
                safe_company = safe_filename(request.company_name)
                filename = f"esg_report_{safe_company}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Output directory (output/)
            output_dir = project_root / "output"
            output_dir.mkdir(exist_ok=True)
            filepath = output_dir / filename
            
            # Progress tracking
            progress_queue = []
            current_step = None
            step_percentages = {
                "Kapak sayfası oluşturuluyor...": 5,
                "Yönetici özeti ekleniyor...": 15,
                "Emisyon özeti ekleniyor...": 25,
                "Grafikler oluşturuluyor...": 35,
                "AI ile içerik üretimi başlatılıyor...": 40,
                "AI içerik üretimi tamamlandı": 50,
                "Detaylı emisyon verileri ekleniyor...": 55,
                "Performans analizi ekleniyor...": 60,
                "Kritik aktivite analizi ekleniyor...": 65,
                "İyileştirme önerileri ekleniyor...": 70,
                "Risk analizi ekleniyor...": 75,
                "Metodoloji bölümü ekleniyor...": 80,
                "Kapanış bölümü ekleniyor...": 85,
                "PDF oluşturuluyor...": 90,
                "Rapor oluşturma tamamlandı!": 100
            }
            
            def progress_callback(message: str):
                """Progress callback - mesajları queue'ya ekle"""
                progress_queue.append(message)
            
            # Start report generation in background thread
            import threading
            
            def generate_report_sync():
                try:
                    generator = ESG_Report_Generator_Fixed(
                        company_name=request.company_name,
                        reporting_period=request.period,
                        use_ai=True,
                        progress_callback=progress_callback
                    )
                    
                    # Get ML results if available (optional)
                    ml_results = None
                    
                    generator.generate_report(
                        emission_results, 
                        scope_summary, 
                        filename,
                        ml_results=ml_results
                    )
                    
                    # Final completion message
                    progress_queue.append("COMPLETE")
                except Exception as e:
                    import traceback
                    error_msg = f"ERROR: {str(e)}\n{traceback.format_exc()}"
                    progress_queue.append(error_msg)
            
            # Start generation in thread
            thread = threading.Thread(target=generate_report_sync, daemon=True)
            thread.start()
            
            # Stream progress messages
            last_percentage = 0
            while True:
                await asyncio.sleep(0.1)  # Check every 100ms
                
                # Process queued messages
                while progress_queue:
                    message = progress_queue.pop(0)
                    
                    if message == "COMPLETE":
                        # Save report metadata
                        try:
                            save_report_metadata(filename, request.company_name, request.period, filepath)
                        except Exception as e:
                            print(f"Warning: Failed to save metadata: {e}")
                        
                        # Send completion message
                        progress_msg = ReportProgressMessage(
                            type="complete",
                            message="Rapor başarıyla oluşturuldu!",
                            step="complete",
                            percentage=100,
                            filename=filename,
                            file_path=str(filepath)
                        )
                        yield f"data: {progress_msg.model_dump_json()}\n\n"
                        return
                    
                    elif message.startswith("ERROR:"):
                        # Send error message
                        error_msg = ReportProgressMessage(
                            type="error",
                            message=message.replace("ERROR: ", ""),
                            step=current_step,
                            percentage=last_percentage
                        )
                        yield f"data: {error_msg.model_dump_json()}\n\n"
                        return
                    
                    else:
                        # Determine step and percentage
                        step_key = None
                        percentage = last_percentage
                        
                        for key, pct in step_percentages.items():
                            if key in message:
                                step_key = key
                                percentage = pct
                                break
                        
                        # Map message to step identifier
                        step_map = {
                            "Kapak sayfası": "cover",
                            "Yönetici özeti": "executive_summary",
                            "Emisyon özeti": "emission_summary",
                            "Grafikler": "charts",
                            "AI ile içerik": "ai_content",
                            "Detaylı emisyon": "detailed_data",
                            "Performans analizi": "performance",
                            "Kritik aktivite": "critical_analysis",
                            "İyileştirme önerileri": "recommendations",
                            "Risk analizi": "risk",
                            "Metodoloji": "methodology",
                            "Kapanış": "closing",
                            "PDF oluşturuluyor": "pdf_generation"
                        }
                        
                        step_id = None
                        for key, step in step_map.items():
                            if key in message:
                                step_id = step
                                break
                        
                        if percentage > last_percentage:
                            last_percentage = percentage
                        
                        current_step = step_id or "unknown"
                        
                        # Send progress message
                        progress_msg = ReportProgressMessage(
                            type="progress",
                            message=message,
                            step=current_step,
                            percentage=percentage
                        )
                        yield f"data: {progress_msg.model_dump_json()}\n\n"
                
                # Check if thread is done
                if not thread.is_alive():
                    if not progress_queue:
                        break
            
            # Wait for thread to complete
            thread.join(timeout=300)  # 5 minute timeout
            
        except Exception as e:
            error_msg = ReportProgressMessage(
                type="error",
                message=f"Rapor oluşturma hatası: {str(e)}",
                step=current_step,
                percentage=last_percentage
            )
            yield f"data: {error_msg.model_dump_json()}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

def save_report_metadata(filename: str, company_name: str, period: str, filepath: Path):
    """Save report metadata to JSON file"""
    metadata_file = project_root / "output" / "reports_metadata.json"
    
    # Load existing metadata
    reports = []
    if metadata_file.exists():
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                reports = json.load(f)
        except:
            reports = []
    
    # Add new report
    report_info = {
        "filename": filename,
        "company_name": company_name,
        "period": period,
        "created_at": datetime.now().isoformat(),
        "file_size": filepath.stat().st_size if filepath.exists() else 0,
        "file_path": str(filepath)
    }
    
    # Remove duplicate if exists (same filename)
    reports = [r for r in reports if r.get("filename") != filename]
    reports.append(report_info)
    
    # Save back
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)
    
    return report_info


@router.get("/report/list", response_model=ReportListResponse)
async def list_reports():
    """List all generated reports"""
    try:
        output_dir = project_root / "output"
        metadata_file = output_dir / "reports_metadata.json"
        
        reports = []
        
        # Try to load from metadata file
        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    reports_data = json.load(f)
                    for r in reports_data:
                        # Verify file still exists
                        file_path = Path(r.get("file_path", ""))
                        if file_path.exists():
                            reports.append(ReportInfo(**r))
            except Exception as e:
                print(f"Error loading metadata: {e}")
        
        # Also scan directory for PDFs not in metadata
        if output_dir.exists():
            for pdf_file in output_dir.glob("*.pdf"):
                # Check if already in reports
                if not any(r.filename == pdf_file.name for r in reports):
                    # Create metadata entry
                    report_info = ReportInfo(
                        filename=pdf_file.name,
                        company_name="Unknown",
                        period="Unknown",
                        created_at=datetime.fromtimestamp(pdf_file.stat().st_mtime).isoformat(),
                        file_size=pdf_file.stat().st_size,
                        file_path=str(pdf_file)
                    )
                    reports.append(report_info)
        
        # Sort by created_at (newest first)
        reports.sort(key=lambda x: x.created_at, reverse=True)
        
        return ReportListResponse(
            success=True,
            reports=reports,
            total_count=len(reports)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing reports: {str(e)}")


@router.delete("/report/delete/{filename:path}", response_model=ReportDeleteResponse)
async def delete_report(filename: str):
    """Delete a generated report"""
    try:
        from urllib.parse import unquote
        filename = unquote(filename)
        
        output_dir = project_root / "output"
        filepath = output_dir / filename
        
        if not filepath.exists():
            raise HTTPException(status_code=404, detail=f"Report not found: {filename}")
        
        # Delete file
        filepath.unlink()
        
        # Remove from metadata
        metadata_file = output_dir / "reports_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    reports = json.load(f)
                
                reports = [r for r in reports if r.get("filename") != filename]
                
                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(reports, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error updating metadata: {e}")
        
        return ReportDeleteResponse(
            success=True,
            message=f"Report deleted successfully: {filename}",
            filename=filename
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting report: {str(e)}")


@router.get("/report/download/{filename:path}")
async def download_report(filename: str):
    """Download generated report"""
    try:
        from urllib.parse import unquote
        import unicodedata
        import re
        
        # URL decode filename
        filename = unquote(filename)
        
        # Safe filename function (same as in generate_stream)
        def safe_filename(text: str) -> str:
            """Convert text to safe filename (no special chars)"""
            text = unicodedata.normalize('NFKD', text)
            text = re.sub(r'[^\w\s-]', '', text)
            text = re.sub(r'[-\s]+', '_', text)
            return text
        
        # Normalize filename (remove any remaining special chars)
        safe_name = safe_filename(filename)
        
        # Check both reports and output directories
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "reports")
        output_dir = project_root / "output"
        
        # Try multiple filename variations
        possible_names = [
            filename,  # Original
            safe_name,  # Safe version
            filename.replace('%C5%9E', 'S').replace('%C4%B1', 'i'),  # Common Turkish chars
        ]
        
        filepath = None
        for name in possible_names:
            # Try output directory first (new location)
            test_path = output_dir / name
            if test_path.exists():
                filepath = test_path
                break
            
            # Try old reports directory
            test_path = Path(os.path.join(reports_dir, name))
            if test_path.exists():
                filepath = test_path
                break
        
        if filepath is None:
            # List available files for debugging
            available_files = []
            if output_dir.exists():
                available_files.extend([f.name for f in output_dir.glob("*.pdf")])
            if Path(reports_dir).exists():
                available_files.extend([f.name for f in Path(reports_dir).glob("*.pdf")])
            
            raise HTTPException(
                status_code=404, 
                detail=f"Report not found: {filename}. Available files: {available_files[:5]}"
            )
        
        return FileResponse(
            str(filepath),
            media_type="application/pdf",
            filename=filepath.name,
            headers={
                "Content-Disposition": f'attachment; filename="{filepath.name}"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

