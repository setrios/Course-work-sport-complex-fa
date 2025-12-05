from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.services.graph_service import GraphService
from app.db.mysql_session import get_db

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/products/{client_id}")
def get_product_recommendations(client_id: int, limit: int = 5):
    """
    Get product recommendations for a client based on Neo4j graph analysis.
    """
    recommendations = GraphService.get_product_recommendations(client_id, limit)
    return {
        "client_id": client_id,
        "recommendations": recommendations
    }

@router.get("/trainers/{client_id}")
def get_trainer_recommendations(client_id: int, limit: int = 5):
    """
    Get trainer recommendations for a client based on Neo4j graph analysis.
    """
    recommendations = GraphService.get_trainer_recommendations(client_id, limit)
    return {
        "client_id": client_id,
        "recommendations": recommendations
    }
