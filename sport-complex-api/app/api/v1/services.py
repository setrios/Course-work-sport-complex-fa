from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.service import ServiceCreate, ServiceResponse
from app.models.service import Service
from app.db.mysql_session import get_db

router = APIRouter(prefix="/services", tags=["Services"])

@router.get("/", response_model=List[ServiceResponse])
def list_services(db: Session = Depends(get_db)):
    """
    Get all services.
    """
    return db.query(Service).all()

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """
    Get a specific service by ID.
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return service

@router.post("/", response_model=ServiceResponse, status_code=201)
def create_service(service_data: ServiceCreate, db: Session = Depends(get_db)):
    """
    Create a new service.
    """
    new_service = Service(**service_data.model_dump())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service
