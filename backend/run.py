"""
Backend entry point - Run from backend directory
"""
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))

if __name__ == "__main__":
    import uvicorn
    
    # Reload için import string kullan (uyarıyı önlemek için)
    uvicorn.run(
        "app.main:app",  # Import string format
        host="0.0.0.0",
        port=8000,
        reload=True
    )

