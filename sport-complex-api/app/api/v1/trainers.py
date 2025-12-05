from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.schemas.trainer import TrainerCreate, TrainerUpdate, TrainerResponse, ScheduleCreate, ScheduleResponse
from app.services.trainer_service import (
    get_trainers, get_trainer_by_id, create_trainer, 
    update_trainer, delete_trainer, create_schedule, get_trainer_schedules
)
from app.db.mysql_session import get_db

router = APIRouter(prefix="/trainers", tags=["Trainers"])

@router.get("/", response_model=List[TrainerResponse])
def list_trainers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all trainers with pagination.
    """
    return get_trainers(db, skip, limit)

@router.get("/{trainer_id}", response_model=TrainerResponse)
def get_trainer(trainer_id: int, db: Session = Depends(get_db)):
    """
    Get a specific trainer by ID.
    """
    return get_trainer_by_id(db, trainer_id)

@router.post("/", response_model=TrainerResponse, status_code=201)
def create_new_trainer(trainer_data: TrainerCreate, db: Session = Depends(get_db)):
    """
    Create a new trainer.
    """
    return create_trainer(db, trainer_data)

@router.patch("/{trainer_id}", response_model=TrainerResponse)
def update_trainer_info(
    trainer_id: int,
    trainer_data: TrainerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update trainer information.
    """
    return update_trainer(db, trainer_id, trainer_data)

@router.delete("/{trainer_id}")
def delete_trainer_by_id(trainer_id: int, db: Session = Depends(get_db)):
    """
    Delete a trainer.
    """
    return delete_trainer(db, trainer_id)

@router.post("/schedules", response_model=ScheduleResponse, status_code=201)
def add_schedule(schedule_data: ScheduleCreate, db: Session = Depends(get_db)):
    """
    Add a schedule for a trainer.
    """
    return create_schedule(db, schedule_data)

@router.get("/{trainer_id}/schedules", response_model=List[ScheduleResponse])
def list_trainer_schedules(trainer_id: int, db: Session = Depends(get_db)):
    """
    Get all schedules for a specific trainer.
    """
    return get_trainer_schedules(db, trainer_id)
