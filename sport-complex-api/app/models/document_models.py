from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class CouchDBDocument:
    """Base class for CouchDB documents"""
    def __init__(self, doc_type: str, **kwargs):
        self._id = kwargs.get('_id', str(uuid.uuid4()))
        self.doc_type = doc_type
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class MedicalCertificate(CouchDBDocument):
    """Medical certificate document for clients"""
    def __init__(self, client_id: int, clinic_id: int, expiry_date: str, 
                 doctor: Dict, examination_results: Dict, **kwargs):
        super().__init__('medical_certificate', **kwargs)
        self.client_id = client_id
        self.clinic_id = clinic_id
        self.expiry_date = expiry_date
        self.doctor = doctor
        self.examination_results = examination_results
        self.status = kwargs.get('status', 'valid')

class TrainingSessionLog(CouchDBDocument):
    """Detailed log of a training session"""
    def __init__(self, session_id: int, trainer_id: int, client_id: int,
                 exercises: list, notes: str, **kwargs):
        super().__init__('training_session_log', **kwargs)
        self.session_id = session_id
        self.trainer_id = trainer_id
        self.client_id = client_id
        self.exercises = exercises  # List of {name, sets, reps, weight}
        self.notes = notes
        self.duration_minutes = kwargs.get('duration_minutes', 0)

class AdministrativeReport(CouchDBDocument):
    """Administrative report document"""
    def __init__(self, report_type: str, generated_by: int, period: Dict,
                 data: Dict, **kwargs):
        super().__init__('administrative_report', **kwargs)
        self.report_type = report_type
        self.generated_by = generated_by
        self.period = period  # {start_date, end_date}
        self.data = data  # Report data
        self.generated_at = kwargs.get('generated_at', datetime.now().isoformat())

class SupplyRequestLetter(CouchDBDocument):
    """Letter to suppliers for product requests"""
    def __init__(self, letter_number: str, supplier: Dict, 
                 products_requested: list, **kwargs):
        super().__init__('supply_request_letter', **kwargs)
        self.letter_number = letter_number
        self.date = kwargs.get('date', datetime.now().strftime('%Y-%m-%d'))
        self.supplier = supplier  # {name, contact, email}
        self.products_requested = products_requested  # List of {product_id, name, quantity}
        self.status = kwargs.get('status', 'pending')
