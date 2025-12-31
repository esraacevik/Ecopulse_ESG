"""
Activity Database API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir.parent))

router = APIRouter()

@router.get("/activity/search")
async def search_activities(
    query: str = Query(..., description="Search query"),
    scope: Optional[str] = Query(None, description="Filter by scope"),
    category: Optional[str] = Query(None, description="Filter by category"),
    region: Optional[str] = Query(None, description="Filter by region"),
    limit: int = Query(50, description="Maximum results")
):
    """Search emission activities in database"""
    try:
        from app.services.activity_database import ActivityDatabase
        
        db = ActivityDatabase()
        results = []
        
        # Convert scope format if needed
        scope_filter = None
        if scope:
            if scope.startswith('Scope '):
                scope_filter = scope.replace('Scope ', '')
            else:
                scope_filter = scope
        
        # Search activities
        activities = db.search_activities(
            query=query,
            scope=scope_filter,
            category=category,
            region=region,
            limit=limit
        )
        
        # Format results
        for activity in activities:
            # Get scope from scopes array or default
            activity_scope = 'Unknown'
            if 'scopes' in activity and activity['scopes']:
                activity_scope = f"Scope {activity['scopes'][0]}"
            elif 'scope' in activity:
                activity_scope = activity['scope']
            
            results.append({
                'id': activity.get('activity_id', ''),
                'name': activity.get('name', ''),
                'category': activity.get('category', ''),
                'scope': activity_scope,
                'region': activity.get('region', 'GLOBAL'),
                'source': activity.get('source', '')
            })
        
        return {
            'results': results[:limit],
            'total': len(results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity/popular")
async def get_popular_activities(limit: int = Query(20, description="Number of results")):
    """Get popular emission activities"""
    try:
        from app.services.activity_database import ActivityDatabase
        
        db = ActivityDatabase()
        popular = db.get_popular_activities(limit=limit)
        
        return {
            'results': popular,
            'total': len(popular)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity/categories")
async def get_categories():
    """Get all available categories"""
    try:
        from app.services.activity_database import ActivityDatabase
        
        db = ActivityDatabase()
        categories = db.get_categories()
        
        return {
            'categories': categories
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

