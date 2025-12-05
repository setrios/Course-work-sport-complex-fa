from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.trainer import Trainer, TrainerSchedule
from app.schemas.trainer import TrainerCreate, TrainerUpdate, ScheduleCreate
from typing import List

def get_trainers(db: Session, skip: int = 0, limit: int = 100) -> List[Trainer]:
    """
    Get all trainers with pagination.
    """
    return db.query(Trainer).offset(skip).limit(limit).all()

def get_trainer_by_id(db: Session, trainer_id: int) -> Trainer:
    """
    Get a trainer by ID.
    """
    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )
    return trainer

def create_trainer(db: Session, trainer_data: TrainerCreate) -> Trainer:
    """
    Create a new trainer in MySQL and Neo4j.
    """
    from app.services.graph_service import GraphService
    
    new_trainer = Trainer(**trainer_data.model_dump())
    db.add(new_trainer)
    db.commit()
    db.refresh(new_trainer)
    
    # Create node in Neo4j
    try:
        full_name = f"{new_trainer.first_name} {new_trainer.last_name}"
        GraphService.create_trainer_node(
            new_trainer.id,
            full_name,
            new_trainer.specialization.value
        )
    except Exception as e:
        print(f"Neo4j error (non-critical): {e}")
    
    return new_trainer

def update_trainer(db: Session, trainer_id: int, trainer_data: TrainerUpdate) -> Trainer:
    """
    Update trainer information.
    """
    trainer = get_trainer_by_id(db, trainer_id)
    
    update_data = trainer_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(trainer, key, value)
    
    db.commit()
    db.refresh(trainer)
    return trainer

def delete_trainer(db: Session, trainer_id: int):
    """
    Delete a trainer.
    """
    trainer = get_trainer_by_id(db, trainer_id)
    db.delete(trainer)
    db.commit()
    return {"message": "Trainer deleted successfully"}

def create_schedule(db: Session, schedule_data: ScheduleCreate) -> TrainerSchedule:
    """
    Create a schedule for a trainer.
    """
    # Verify trainer exists
    get_trainer_by_id(db, schedule_data.trainer_id)
    
    new_schedule = TrainerSchedule(**schedule_data.model_dump())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule

def get_trainer_schedules(db: Session, trainer_id: int) -> List[TrainerSchedule]:
    """
    Get all schedules for a trainer.
    """
    return db.query(TrainerSchedule).filter(
        TrainerSchedule.trainer_id == trainer_id,
        TrainerSchedule.is_active == True
    ).all()
