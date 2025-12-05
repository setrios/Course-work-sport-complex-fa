from fastapi import APIRouter
from typing import List, Dict
from app.services.document_service import DocumentService
from pydantic import BaseModel

router = APIRouter(prefix="/documents", tags=["Documents"])

# Pydantic models for request validation
class MedicalCertificateCreate(BaseModel):
    client_id: int
    clinic_id: int
    expiry_date: str
    doctor: Dict
    examination_results: Dict

class SessionLogCreate(BaseModel):
    session_id: int
    trainer_id: int
    client_id: int
    exercises: List[Dict]
    notes: str
    duration_minutes: int = 0

class AdminReportCreate(BaseModel):
    report_type: str
    generated_by: int
    period: Dict
    data: Dict

@router.post("/medical-certificates", status_code=201)
def create_certificate(cert_data: MedicalCertificateCreate):
    """
    Create a medical certificate in CouchDB.
    """
    doc_id = DocumentService.create_medical_certificate(
        cert_data.client_id,
        cert_data.clinic_id,
        cert_data.expiry_date,
        cert_data.doctor,
        cert_data.examination_results
    )
    return {"document_id": doc_id, "message": "Certificate created"}

@router.get("/medical-certificates/{doc_id}")
def get_certificate(doc_id: str):
    """
    Get a medical certificate by ID.
    """
    doc = DocumentService.get_medical_certificate(doc_id)
    if not doc:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Certificate not found")
    return doc

@router.get("/medical-certificates/client/{client_id}")
def get_client_certificates(client_id: int):
    """
    Get all medical certificates for a client.
    """
    certs = DocumentService.get_client_certificates(client_id)
    return {"client_id": client_id, "certificates": certs}

@router.post("/session-logs", status_code=201)
def create_log(log_data: SessionLogCreate):
    """
    Create a training session log in CouchDB.
    """
    doc_id = DocumentService.create_session_log(
        log_data.session_id,
        log_data.trainer_id,
        log_data.client_id,
        log_data.exercises,
        log_data.notes,
        log_data.duration_minutes
    )
    return {"document_id": doc_id, "message": "Session log created"}

@router.get("/session-logs/{doc_id}")
def get_log(doc_id: str):
    """
    Get a session log by ID.
    """
    doc = DocumentService.get_session_log(doc_id)
    if not doc:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Log not found")
    return doc

@router.post("/reports", status_code=201)
def create_report(report_data: AdminReportCreate):
    """
    Create an administrative report in CouchDB.
    """
    doc_id = DocumentService.create_admin_report(
        report_data.report_type,
        report_data.generated_by,
        report_data.period,
        report_data.data
    )
    return {"document_id": doc_id, "message": "Report created"}

@router.get("/reports/{doc_id}")
def get_report(doc_id: str):
    """
    Get an administrative report by ID.
    """
    doc = DocumentService.get_admin_report(doc_id)
    if not doc:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Report not found")
    return doc
