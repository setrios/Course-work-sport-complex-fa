from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

# Helper to generate UUIDs
def generate_uuid():
    return str(uuid.uuid4())

# ============ DOCUMENT MODELS ============

class CouchDBDocument:
    def __init__(self, doc_type: str, **kwargs):
        self._id = kwargs.get('_id', generate_uuid())
        self.type = doc_type
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        for key, value in kwargs.items():
            if key not in ['_id', 'type', 'created_at']:
                setattr(self, key, value)

    def to_json(self) -> Dict[str, Any]:
        return self.__dict__

class MedicalCertificate(CouchDBDocument):
    def __init__(self, client_id: int, clinic_id: int, expiry_date: str, doctor: Dict, examination_results: Dict, **kwargs):
        super().__init__('medical_certificate', **kwargs)
        self.client_id = client_id
        self.clinic_id = clinic_id
        self.expiry_date = expiry_date
        self.doctor = doctor
        self.examination_results = examination_results
        self.status = kwargs.get('status', 'valid')
        self._attachments = kwargs.get('_attachments', {})

class AdministrativeReport(CouchDBDocument):
    def __init__(self, title: str, period: Dict[str, str], services: List[Dict], generated_by: str, **kwargs):
        super().__init__('services_popularity_report', **kwargs)
        self.title = title
        self.period = period
        self.services = services
        self.generated_by = generated_by
        self.recommendations = kwargs.get('recommendations', [])
        self.charts_data = kwargs.get('charts_data', {})

class SupplyRequestLetter(CouchDBDocument):
    def __init__(self, letter_number: str, supplier: Dict, products_requested: List[Dict], **kwargs):
        super().__init__('supply_request_letter', **kwargs)
        self.letter_number = letter_number
        self.date = kwargs.get('date', datetime.now().strftime('%Y-%m-%d'))
        self.supplier = supplier
        self.products_requested = products_requested
        self.status = kwargs.get('status', 'pending') # pending, sent
        self.order_summary = kwargs.get('order_summary', {})
        self.delivery_requirements = kwargs.get('delivery_requirements', {})

class TrainingSessionLog(CouchDBDocument):
    def __init__(self, session_id: int, client_id: int, trainer_id: int, exercises_performed: List[Dict], **kwargs):
        super().__init__('training_session_log', **kwargs)
        self.session_id = session_id
        self.client_id = client_id
        self.trainer_id = trainer_id
        self.exercises_performed = exercises_performed
        self.session_details = kwargs.get('session_details', {})
        self.client_metrics = kwargs.get('client_metrics', {})
        self.trainer_notes = kwargs.get('trainer_notes', "")

# ============ FACTORY / USAGE EXAMPLES ============

def create_sample_medical_cert():
    return MedicalCertificate(
        client_id=123,
        clinic_id=5,
        expiry_date="2025-12-01",
        doctor={"name": "Dr. House", "license": "LIC123456"},
        examination_results={"blood_pressure": "120/80", "pool_approved": True}
    )

def create_sample_supply_request():
    return SupplyRequestLetter(
        letter_number="REQ-2024-001",
        supplier={"id": 15, "name": "NutritionPro", "email": "orders@nutritionpro.ua"},
        products_requested=[
            {"product_id": 45, "name": "Whey Protein", "requested_quantity": 20}
        ]
    )
