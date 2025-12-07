"""Sport Complex System - Core Classes"""
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional


class Gender(str, Enum):
    """Gender enumeration"""
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


@dataclass
class ContactInfo:
    """Contact information data class"""
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


@dataclass
class Client:
    """Client entity"""
    client_id: str
    full_name: str
    birth_date: any
    gender: str
    contact_info: ContactInfo
    has_valid_cert: bool = False


@dataclass
class Trainer:
    """Trainer entity"""
    trainer_id: str
    full_name: str
    specialization: str
    contact_info: ContactInfo
    certification_level: Optional[str] = None


class SportComplexSystem:
    """In-memory sport complex management system"""
    
    def __init__(self):
        self.clients: Dict[str, Client] = {}
        self.trainers: Dict[str, Trainer] = {}
        self.services: Dict[str, dict] = {}
        self.bookings: Dict[str, dict] = {}
        self.memberships: Dict[str, dict] = {}
        self._next_client_id = 1
        self._next_trainer_id = 1
    
    def add_client_entity(
        self, 
        full_name: str, 
        birth_date: any, 
        gender: str, 
        contact: ContactInfo,
        username: Optional[str] = None
    ) -> Client:
        """Add a client entity to the system"""
        client_id = username or f"client_{self._next_client_id}"
        self._next_client_id += 1
        
        client = Client(
            client_id=client_id,
            full_name=full_name,
            birth_date=birth_date,
            gender=gender,
            contact_info=contact,
            has_valid_cert=False
        )
        self.clients[client_id] = client
        return client
    
    def add_trainer_entity(
        self,
        full_name: str,
        specialization: str,
        contact: ContactInfo,
        certification_level: Optional[str] = None
    ) -> Trainer:
        """Add a trainer entity to the system"""
        trainer_id = f"trainer_{self._next_trainer_id}"
        self._next_trainer_id += 1
        
        trainer = Trainer(
            trainer_id=trainer_id,
            full_name=full_name,
            specialization=specialization,
            contact_info=contact,
            certification_level=certification_level
        )
        self.trainers[trainer_id] = trainer
        return trainer
    
    def add_client(self, client_data: dict) -> dict:
        """Add a client to the system (legacy dict-based method)"""
        client_id = client_data.get("client_id") or f"client_{self._next_client_id}"
        self._next_client_id += 1
        client_data["client_id"] = client_id
        
        contact_info = ContactInfo(**client_data.get("contact_info", {}))
        client = Client(
            client_id=client_id,
            full_name=client_data["full_name"],
            birth_date=client_data["birth_date"],
            gender=client_data["gender"],
            contact_info=contact_info
        )
        self.clients[client_id] = client
        return client_data
    
    def get_clients(self) -> list:
        """Get all clients as list"""
        return list(self.clients.values())
    
    def add_trainer(self, trainer_data: dict) -> dict:
        """Add a trainer to the system (legacy dict-based method)"""
        trainer_id = trainer_data.get("trainer_id") or f"trainer_{self._next_trainer_id}"
        self._next_trainer_id += 1
        trainer_data["trainer_id"] = trainer_id
        return trainer_data
    
    def get_trainers(self) -> list:
        """Get all trainers as list"""
        return list(self.trainers.values())
    
    def add_service(self, service_data: dict) -> dict:
        """Add a service to the system"""
        service_id = service_data.get("service_id") or f"service_{len(self.services) + 1}"
        service_data["service_id"] = service_id
        self.services[service_id] = service_data
        return service_data
    
    def get_services(self) -> list:
        """Get all services"""
        return list(self.services.values())
    
    def add_booking(self, booking_data: dict) -> dict:
        """Add a booking to the system"""
        booking_id = booking_data.get("booking_id") or f"booking_{len(self.bookings) + 1}"
        booking_data["booking_id"] = booking_id
        self.bookings[booking_id] = booking_data
        return booking_data
    
    def get_bookings(self) -> list:
        """Get all bookings"""
        return list(self.bookings.values())
    
    def add_membership(self, membership_data: dict) -> dict:
        """Add a membership to the system"""
        membership_id = membership_data.get("membership_id") or f"membership_{len(self.memberships) + 1}"
        membership_data["membership_id"] = membership_id
        self.memberships[membership_id] = membership_data
        return membership_data
    
    def get_memberships(self) -> list:
        """Get all memberships"""
        return list(self.memberships.values())
