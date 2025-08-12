"""Patient Management Agent - Handles all patient-related operations"""

import uuid
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from .base_agent import BaseAgent

try:
    from database import Patient, SessionLocal
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


class PatientAgent(BaseAgent):
    """Agent specialized in patient management operations"""
    
    def __init__(self):
        super().__init__("Patient Management Agent", "patient_agent")
    
    def get_tools(self) -> List[str]:
        """Return list of patient management tools"""
        return [
            "create_patient",
            "list_patients",
            "get_patient_by_id",
            "search_patients",
            "update_patient",
            "delete_patient"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Return list of patient management capabilities"""
        return [
            "Patient registration and admission",
            "Medical records management",
            "Patient information retrieval and search",
            "Patient demographics tracking",
            "Emergency contact management",
            "Medical history and allergy tracking"
        ]
    
    def create_patient(self, first_name: str, last_name: str, date_of_birth: str,
                      gender: str = None, phone: str = None, email: str = None,
                      address: str = None, emergency_contact_name: str = None,
                      emergency_contact_phone: str = None, blood_type: str = None,
                      allergies: str = None, medical_history: str = None) -> Dict[str, Any]:
        """Create a new patient record."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            # Generate unique patient number
            import random
            patient_number = f"P{random.randint(100000, 999999)}"
            
            # Parse date of birth
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
            
            db = self.get_db_session()
            patient = Patient(
                patient_number=patient_number,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                gender=gender,
                phone=phone,
                email=email,
                address=address,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_phone=emergency_contact_phone,
                blood_type=blood_type,
                allergies=allergies,
                medical_history=medical_history
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
            result = self.serialize_model(patient)
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Create patient: {first_name} {last_name}",
                response=f"Patient created successfully with number: {patient_number}",
                tool_used="create_patient"
            )
            
            return {"success": True, "message": "Patient created successfully", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to create patient: {str(e)}"}

    def list_patients(self) -> Dict[str, Any]:
        """List all patients."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            db = self.get_db_session()
            patients = db.query(Patient).all()
            result = [self.serialize_model(patient) for patient in patients]
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query="List all patients",
                response=f"Found {len(result)} patients",
                tool_used="list_patients"
            )
            
            return {"data": result}
        except Exception as e:
            return {"error": f"Failed to list patients: {str(e)}"}

    def get_patient_by_id(self, patient_id: str) -> Dict[str, Any]:
        """Get a patient by ID."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            db = self.get_db_session()
            patient = db.query(Patient).filter(Patient.id == uuid.UUID(patient_id)).first()
            result = self.serialize_model(patient) if patient else None
            db.close()
            
            if result:
                # Log the interaction
                self.log_interaction(
                    query=f"Get patient by ID: {patient_id}",
                    response=f"Patient found: {result.get('first_name', '')} {result.get('last_name', '')}",
                    tool_used="get_patient_by_id"
                )
                return {"data": result}
            else:
                return {"error": "Patient not found"}
        except Exception as e:
            return {"error": f"Failed to get patient: {str(e)}"}

    def search_patients(self, patient_number: str = None, first_name: str = None, 
                       last_name: str = None, phone: str = None, email: str = None) -> Dict[str, Any]:
        """Search for patients by various criteria."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            db = self.get_db_session()
            query = db.query(Patient)
            
            # Build search filters
            filters = []
            search_criteria = []
            
            if patient_number:
                filters.append(Patient.patient_number.ilike(f"%{patient_number}%"))
                search_criteria.append(f"patient_number: {patient_number}")
            if first_name:
                filters.append(Patient.first_name.ilike(f"%{first_name}%"))
                search_criteria.append(f"first_name: {first_name}")
            if last_name:
                filters.append(Patient.last_name.ilike(f"%{last_name}%"))
                search_criteria.append(f"last_name: {last_name}")
            if phone:
                filters.append(Patient.phone.ilike(f"%{phone}%"))
                search_criteria.append(f"phone: {phone}")
            if email:
                filters.append(Patient.email.ilike(f"%{email}%"))
                search_criteria.append(f"email: {email}")
            
            # Apply filters
            if filters:
                query = query.filter(or_(*filters))
            
            patients = query.all()
            result = [self.serialize_model(patient) for patient in patients]
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Search patients: {', '.join(search_criteria)}",
                response=f"Found {len(result)} matching patients",
                tool_used="search_patients"
            )
            
            return {"data": result}
        except Exception as e:
            return {"error": f"Failed to search patients: {str(e)}"}

    def update_patient(self, patient_id: str, first_name: str = None, last_name: str = None,
                      gender: str = None, phone: str = None, email: str = None,
                      address: str = None, emergency_contact_name: str = None,
                      emergency_contact_phone: str = None, blood_type: str = None,
                      allergies: str = None, medical_history: str = None) -> Dict[str, Any]:
        """Update patient information."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            db = self.get_db_session()
            patient = db.query(Patient).filter(Patient.id == uuid.UUID(patient_id)).first()
            
            if not patient:
                db.close()
                return {"success": False, "message": "Patient not found"}
            
            # Update provided fields
            update_fields = []
            if first_name is not None:
                patient.first_name = first_name
                update_fields.append("first_name")
            if last_name is not None:
                patient.last_name = last_name
                update_fields.append("last_name")
            if gender is not None:
                patient.gender = gender
                update_fields.append("gender")
            if phone is not None:
                patient.phone = phone
                update_fields.append("phone")
            if email is not None:
                patient.email = email
                update_fields.append("email")
            if address is not None:
                patient.address = address
                update_fields.append("address")
            if emergency_contact_name is not None:
                patient.emergency_contact_name = emergency_contact_name
                update_fields.append("emergency_contact_name")
            if emergency_contact_phone is not None:
                patient.emergency_contact_phone = emergency_contact_phone
                update_fields.append("emergency_contact_phone")
            if blood_type is not None:
                patient.blood_type = blood_type
                update_fields.append("blood_type")
            if allergies is not None:
                patient.allergies = allergies
                update_fields.append("allergies")
            if medical_history is not None:
                patient.medical_history = medical_history
                update_fields.append("medical_history")
            
            db.commit()
            db.refresh(patient)
            result = self.serialize_model(patient)
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Update patient {patient_id}: {', '.join(update_fields)}",
                response=f"Patient updated successfully",
                tool_used="update_patient"
            )
            
            return {"success": True, "message": "Patient updated successfully", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to update patient: {str(e)}"}

    def delete_patient(self, patient_id: str) -> Dict[str, Any]:
        """Delete a patient record."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            db = self.get_db_session()
            patient = db.query(Patient).filter(Patient.id == uuid.UUID(patient_id)).first()
            
            if not patient:
                db.close()
                return {"success": False, "message": "Patient not found"}
            
            patient_name = f"{patient.first_name} {patient.last_name}"  # Store for logging
            db.delete(patient)
            db.commit()
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Delete patient: {patient_id}",
                response=f"Patient {patient_name} deleted successfully",
                tool_used="delete_patient"
            )
            
            return {"success": True, "message": "Patient deleted successfully"}
        except Exception as e:
            return {"success": False, "message": f"Failed to delete patient: {str(e)}"}
