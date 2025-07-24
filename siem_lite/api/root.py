from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_root() -> dict:
    return {
        "message": "Welcome to SIEM Lite API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "create_alert": "POST /api/alerts",
            "get_alerts": "GET /api/alerts",
            "get_alert": "GET /api/alerts/{id}",
            "get_stats": "GET /api/stats",
        },
    }
