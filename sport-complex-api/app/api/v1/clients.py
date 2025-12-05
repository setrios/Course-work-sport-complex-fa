from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.schemas.service import TrainingSessionResponse
from app.schemas.order import OrderResponse
from app.services.client_service import (
    get_clients, get_client_by_id, create_client, 
    update_client, delete_client, get_client_sessions, get_client_orders
)
from app.db.mysql_session import get_db

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.get("/", response_model=List[ClientResponse])
def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all clients with pagination.
    """
    return get_clients(db, skip, limit)

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """
    Get a specific client by ID.
    """
    return get_client_by_id(db, client_id)

@router.post("/", response_model=ClientResponse, status_code=201)
def create_new_client(client_data: ClientCreate, db: Session = Depends(get_db)):
    """
    Create a new client.
    """
    return create_client(db, client_data)

@router.patch("/{client_id}", response_model=ClientResponse)
def update_client_info(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db)
):
    """
    Update client information.
    """
    return update_client(db, client_id, client_data)

@router.delete("/{client_id}")
def delete_client_by_id(client_id: int, db: Session = Depends(get_db)):
    """
    Delete a client.
    """
    return delete_client(db, client_id)

@router.get("/{client_id}/sessions", response_model=List[TrainingSessionResponse])
def list_client_sessions(client_id: int, db: Session = Depends(get_db)):
    """
    Get all training sessions for a specific client.
    """
    return get_client_sessions(db, client_id)

@router.get("/{client_id}/orders", response_model=List[OrderResponse])
def list_client_orders(client_id: int, db: Session = Depends(get_db)):
    """
    Get all orders for a specific client.
    """
    return get_client_orders(db, client_id)
