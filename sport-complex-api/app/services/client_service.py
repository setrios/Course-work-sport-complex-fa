from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.client import Client
from app.models.service import TrainingSession
from app.models.order import Order
from app.schemas.client import ClientCreate, ClientUpdate
from typing import List
from datetime import date

def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[Client]:
    """
    Get all clients with pagination.
    """
    return db.query(Client).offset(skip).limit(limit).all()

def get_client_by_id(db: Session, client_id: int) -> Client:
    """
    Get a client by ID.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client

def create_client(db: Session, client_data: ClientCreate) -> Client:
    """
    Create a new client in MySQL and Neo4j.
    """
    from app.services.graph_service import GraphService
    
    new_client = Client(
        **client_data.model_dump(),
        registration_date=date.today()
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    # Create node in Neo4j
    try:
        full_name = f"{new_client.first_name} {new_client.last_name}"
        GraphService.create_client_node(
            new_client.id, 
            full_name, 
            str(new_client.registration_date)
        )
    except Exception as e:
        print(f"Neo4j error (non-critical): {e}")
    
    return new_client

def update_client(db: Session, client_id: int, client_data: ClientUpdate) -> Client:
    """
    Update client information.
    """
    client = get_client_by_id(db, client_id)
    
    update_data = client_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)
    
    db.commit()
    db.refresh(client)
    return client

def delete_client(db: Session, client_id: int):
    """
    Delete a client.
    """
    client = get_client_by_id(db, client_id)
    db.delete(client)
    db.commit()
    return {"message": "Client deleted successfully"}

def get_client_sessions(db: Session, client_id: int) -> List[TrainingSession]:
    """
    Get all training sessions for a client.
    """
    # Verify client exists
    get_client_by_id(db, client_id)
    
    return db.query(TrainingSession).filter(
        TrainingSession.client_id == client_id
    ).all()

def get_client_orders(db: Session, client_id: int) -> List[Order]:
    """
    Get all orders for a client.
    """
    # Verify client exists
    get_client_by_id(db, client_id)
    
    return db.query(Order).filter(
        Order.client_id == client_id
    ).all()
