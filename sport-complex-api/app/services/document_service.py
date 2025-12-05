from typing import Optional, Dict, Any, List
from app.db.couchdb_client import CouchDBClient
from app.models.document_models import (
    MedicalCertificate, TrainingSessionLog, 
    AdministrativeReport, SupplyRequestLetter
)

class DocumentService:
    """Service for CouchDB document operations"""
    
    DB_NAME = "sportcomplex_documents"
    
    @staticmethod
    def _get_db():
        """Get CouchDB database"""
        return CouchDBClient.get_db(DocumentService.DB_NAME)
    
    # Medical Certificates
    @staticmethod
    def create_medical_certificate(client_id: int, clinic_id: int,
                                   expiry_date: str, doctor: Dict,
                                   examination_results: Dict) -> str:
        """Create a medical certificate document"""
        db = DocumentService._get_db()
        cert = MedicalCertificate(
            client_id=client_id,
            clinic_id=clinic_id,
            expiry_date=expiry_date,
            doctor=doctor,
            examination_results=examination_results
        )
        doc_id, _ = db.save(cert.to_dict())
        return doc_id
    
    @staticmethod
    def get_medical_certificate(doc_id: str) -> Optional[Dict]:
        """Get a medical certificate by ID"""
        db = DocumentService._get_db()
        return db.get(doc_id) if doc_id in db else None
    
    @staticmethod
    def get_client_certificates(client_id: int) -> List[Dict]:
        """Get all medical certificates for a client"""
        db = DocumentService._get_db()
        # Create a view if needed, for now use simple iteration
        results = []
        for doc_id in db:
            doc = db[doc_id]
            if doc.get('doc_type') == 'medical_certificate' and doc.get('client_id') == client_id:
                results.append(doc)
        return results
    
    # Training Session Logs
    @staticmethod
    def create_session_log(session_id: int, trainer_id: int, client_id: int,
                          exercises: List[Dict], notes: str, duration_minutes: int = 0) -> str:
        """Create a training session log"""
        db = DocumentService._get_db()
        log = TrainingSessionLog(
            session_id=session_id,
            trainer_id=trainer_id,
            client_id=client_id,
            exercises=exercises,
            notes=notes,
            duration_minutes=duration_minutes
        )
        doc_id, _ = db.save(log.to_dict())
        return doc_id
    
    @staticmethod
    def get_session_log(doc_id: str) -> Optional[Dict]:
        """Get a session log by ID"""
        db = DocumentService._get_db()
        return db.get(doc_id) if doc_id in db else None
    
    # Administrative Reports
    @staticmethod
    def create_admin_report(report_type: str, generated_by: int,
                           period: Dict, data: Dict) -> str:
        """Create an administrative report"""
        db = DocumentService._get_db()
        report = AdministrativeReport(
            report_type=report_type,
            generated_by=generated_by,
            period=period,
            data=data
        )
        doc_id, _ = db.save(report.to_dict())
        return doc_id
    
    @staticmethod
    def get_admin_report(doc_id: str) -> Optional[Dict]:
        """Get an admin report by ID"""
        db = DocumentService._get_db()
        return db.get(doc_id) if doc_id in db else None
    
    # Supply Request Letters
    @staticmethod
    def create_supply_request(letter_number: str, supplier: Dict,
                             products_requested: List[Dict]) -> str:
        """Create a supply request letter"""
        db = DocumentService._get_db()
        letter = SupplyRequestLetter(
            letter_number=letter_number,
            supplier=supplier,
            products_requested=products_requested
        )
        doc_id, _ = db.save(letter.to_dict())
        return doc_id
    
    @staticmethod
    def get_supply_request(doc_id: str) -> Optional[Dict]:
        """Get a supply request by ID"""
        db = DocumentService._get_db()
        return db.get(doc_id) if doc_id in db else None
