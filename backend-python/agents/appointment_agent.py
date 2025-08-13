"""Appointment Management Agent - Handles all appointment-related operations"""

import uuid
from datetime import datetime, date, time
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from .base_agent import BaseAgent

try:
    from database import Appointment, Patient, User, Department, SessionLocal
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


class AppointmentAgent(BaseAgent):
    """Agent specialized in appointment management operations"""
    
    def __init__(self):
        super().__init__("Appointment Management Agent", "appointment_agent")
    
    def get_tools(self) -> List[str]:
        """Return list of appointment management tools"""
        return [
            "create_appointment",
            "list_appointments",
            "get_appointment_by_id",
            "update_appointment",
            "cancel_appointment",
            "reschedule_appointment",
            "get_doctor_schedule",
            "get_patient_appointments",
            "check_appointment_conflicts",
            "get_available_slots"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Return list of appointment management capabilities"""
        return [
            "Patient appointment scheduling",
            "Doctor schedule management",
            "Appointment conflict detection",
            "Appointment rescheduling and cancellation",
            "Available time slot identification",
            "Appointment status tracking"
        ]
    
    def create_appointment(self, patient_id: str, doctor_id: str, department_id: str, 
                          appointment_date: str, appointment_time: str, reason: str = None,
                          notes: str = None, duration_minutes: int = 30, status: str = "scheduled") -> Dict[str, Any]:
        """Create a new appointment."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            # Parse date and time into single datetime
            appt_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
            appt_time = datetime.strptime(appointment_time, "%H:%M").time()
            appt_datetime = datetime.combine(appt_date, appt_time)
            
            # Check for conflicts
            conflict_check = self.check_appointment_conflicts(doctor_id, appointment_date, appointment_time)
            if conflict_check.get("conflict"):
                return {"success": False, "message": f"Appointment conflict detected: {conflict_check.get('message')}"}
            
            db = self.get_db_session()
            appointment = Appointment(
                patient_id=uuid.UUID(patient_id),
                doctor_id=uuid.UUID(doctor_id),
                department_id=uuid.UUID(department_id),
                appointment_date=appt_datetime,
                duration_minutes=duration_minutes,
                reason=reason,
                notes=notes,
                status=status
            )
            db.add(appointment)
            db.commit()
            db.refresh(appointment)
            result = self.serialize_model(appointment)
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Create appointment: Patient {patient_id} with Doctor {doctor_id} on {appointment_date} at {appointment_time}",
                response=f"Appointment created successfully with ID: {result['id']}",
                tool_used="create_appointment"
            )
            
            return {"success": True, "message": "Appointment created successfully", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to create appointment: {str(e)}"}

    def list_appointments(self, doctor_id: str = None, patient_id: str = None, 
                         date: str = None, status: str = None, 
                         department_id: str = None) -> Dict[str, Any]:
        """List appointments with optional filtering."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            db = self.get_db_session()
            query = db.query(Appointment)
            
            filters = []
            if doctor_id:
                query = query.filter(Appointment.doctor_id == uuid.UUID(doctor_id))
                filters.append(f"doctor_id: {doctor_id}")
            if patient_id:
                query = query.filter(Appointment.patient_id == uuid.UUID(patient_id))
                filters.append(f"patient_id: {patient_id}")
            if date:
                appt_date = datetime.strptime(date, "%Y-%m-%d").date()
                query = query.filter(Appointment.appointment_date == appt_date)
                filters.append(f"date: {date}")
            if status:
                query = query.filter(Appointment.status == status)
                filters.append(f"status: {status}")
            if department_id:
                query = query.filter(Appointment.department_id == uuid.UUID(department_id))
                filters.append(f"department_id: {department_id}")
            
            # Order by appointment date and time
            query = query.order_by(Appointment.appointment_date, Appointment.appointment_time)
            
            appointments = query.all()
            result = [self.serialize_model(appointment) for appointment in appointments]
            db.close()
            
            # Log the interaction
            filter_text = f" with filters: {', '.join(filters)}" if filters else ""
            self.log_interaction(
                query=f"List appointments{filter_text}",
                response=f"Found {len(result)} appointments",
                tool_used="list_appointments"
            )
            
            return {"data": result}
        except Exception as e:
            return {"error": f"Failed to list appointments: {str(e)}"}

    def get_appointment_by_id(self, appointment_id: str) -> Dict[str, Any]:
        """Get an appointment by ID."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            db = self.get_db_session()
            appointment = db.query(Appointment).filter(Appointment.id == uuid.UUID(appointment_id)).first()
            result = self.serialize_model(appointment) if appointment else None
            db.close()
            
            if result:
                # Log the interaction
                self.log_interaction(
                    query=f"Get appointment by ID: {appointment_id}",
                    response=f"Appointment found: {result.get('appointment_date')} at {result.get('appointment_time')}",
                    tool_used="get_appointment_by_id"
                )
                return {"data": result}
            else:
                return {"error": "Appointment not found"}
        except Exception as e:
            return {"error": f"Failed to get appointment: {str(e)}"}

    def update_appointment(self, appointment_id: str, appointment_date: str = None,
                          appointment_time: str = None, purpose: str = None,
                          notes: str = None, status: str = None) -> Dict[str, Any]:
        """Update appointment information."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            db = self.get_db_session()
            appointment = db.query(Appointment).filter(Appointment.id == uuid.UUID(appointment_id)).first()
            
            if not appointment:
                db.close()
                return {"success": False, "message": "Appointment not found"}
            
            # Update provided fields
            update_fields = []
            if appointment_date is not None:
                appointment.appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
                update_fields.append("appointment_date")
            if appointment_time is not None:
                appointment.appointment_time = datetime.strptime(appointment_time, "%H:%M").time()
                update_fields.append("appointment_time")
            if purpose is not None:
                appointment.purpose = purpose
                update_fields.append("purpose")
            if notes is not None:
                appointment.notes = notes
                update_fields.append("notes")
            if status is not None:
                appointment.status = status
                update_fields.append("status")
            
            # Check for conflicts if date/time changed
            if appointment_date or appointment_time:
                conflict_check = self.check_appointment_conflicts(
                    str(appointment.doctor_id), 
                    appointment.appointment_date.strftime("%Y-%m-%d"),
                    appointment.appointment_time.strftime("%H:%M"),
                    exclude_appointment_id=appointment_id
                )
                if conflict_check.get("conflict"):
                    db.close()
                    return {"success": False, "message": f"Appointment conflict detected: {conflict_check.get('message')}"}
            
            db.commit()
            db.refresh(appointment)
            result = self.serialize_model(appointment)
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Update appointment {appointment_id}: {', '.join(update_fields)}",
                response=f"Appointment updated successfully",
                tool_used="update_appointment"
            )
            
            return {"success": True, "message": "Appointment updated successfully", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to update appointment: {str(e)}"}

    def cancel_appointment(self, appointment_id: str, cancellation_reason: str = None) -> Dict[str, Any]:
        """Cancel an appointment."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            db = self.get_db_session()
            appointment = db.query(Appointment).filter(Appointment.id == uuid.UUID(appointment_id)).first()
            
            if not appointment:
                db.close()
                return {"success": False, "message": "Appointment not found"}
            
            appointment.status = "cancelled"
            if cancellation_reason:
                appointment.notes = f"{appointment.notes or ''}\nCancellation reason: {cancellation_reason}".strip()
            
            db.commit()
            db.refresh(appointment)
            result = self.serialize_model(appointment)
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Cancel appointment {appointment_id}" + (f": {cancellation_reason}" if cancellation_reason else ""),
                response=f"Appointment cancelled successfully",
                tool_used="cancel_appointment"
            )
            
            return {"success": True, "message": "Appointment cancelled successfully", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to cancel appointment: {str(e)}"}

    def reschedule_appointment(self, appointment_id: str, new_date: str, new_time: str) -> Dict[str, Any]:
        """Reschedule an appointment to a new date and time."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            db = self.get_db_session()
            appointment = db.query(Appointment).filter(Appointment.id == uuid.UUID(appointment_id)).first()
            
            if not appointment:
                db.close()
                return {"success": False, "message": "Appointment not found"}
            
            # Check for conflicts at new time
            conflict_check = self.check_appointment_conflicts(
                str(appointment.doctor_id), 
                new_date, 
                new_time,
                exclude_appointment_id=appointment_id
            )
            if conflict_check.get("conflict"):
                db.close()
                return {"success": False, "message": f"Cannot reschedule - conflict detected: {conflict_check.get('message')}"}
            
            old_date = appointment.appointment_date
            old_time = appointment.appointment_time
            
            appointment.appointment_date = datetime.strptime(new_date, "%Y-%m-%d").date()
            appointment.appointment_time = datetime.strptime(new_time, "%H:%M").time()
            appointment.notes = f"{appointment.notes or ''}\nRescheduled from {old_date} {old_time} to {new_date} {new_time}".strip()
            
            db.commit()
            db.refresh(appointment)
            result = self.serialize_model(appointment)
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Reschedule appointment {appointment_id} from {old_date} {old_time} to {new_date} {new_time}",
                response=f"Appointment rescheduled successfully",
                tool_used="reschedule_appointment"
            )
            
            return {"success": True, "message": "Appointment rescheduled successfully", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to reschedule appointment: {str(e)}"}

    def get_doctor_schedule(self, doctor_id: str, date: str = None) -> Dict[str, Any]:
        """Get a doctor's appointment schedule for a specific date or today."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            appt_date = datetime.strptime(date, "%Y-%m-%d").date()
            
            db = self.get_db_session()
            appointments = db.query(Appointment).filter(
                and_(
                    Appointment.doctor_id == uuid.UUID(doctor_id),
                    Appointment.appointment_date == appt_date,
                    Appointment.status.in_(["scheduled", "confirmed"])
                )
            ).order_by(Appointment.appointment_time).all()
            
            result = [self.serialize_model(appointment) for appointment in appointments]
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Get doctor schedule: {doctor_id} for {date}",
                response=f"Found {len(result)} appointments",
                tool_used="get_doctor_schedule"
            )
            
            return {"data": result, "date": date, "doctor_id": doctor_id}
        except Exception as e:
            return {"error": f"Failed to get doctor schedule: {str(e)}"}

    def get_patient_appointments(self, patient_id: str, status: str = None) -> Dict[str, Any]:
        """Get all appointments for a specific patient."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            db = self.get_db_session()
            query = db.query(Appointment).filter(Appointment.patient_id == uuid.UUID(patient_id))
            
            if status:
                query = query.filter(Appointment.status == status)
            
            appointments = query.order_by(
                Appointment.appointment_date.desc(), 
                Appointment.appointment_time.desc()
            ).all()
            
            result = [self.serialize_model(appointment) for appointment in appointments]
            db.close()
            
            # Log the interaction
            status_filter = f" with status: {status}" if status else ""
            self.log_interaction(
                query=f"Get patient appointments: {patient_id}{status_filter}",
                response=f"Found {len(result)} appointments",
                tool_used="get_patient_appointments"
            )
            
            return {"data": result, "patient_id": patient_id}
        except Exception as e:
            return {"error": f"Failed to get patient appointments: {str(e)}"}

    def check_appointment_conflicts(self, doctor_id: str, appointment_date: str, 
                                   appointment_time: str, exclude_appointment_id: str = None) -> Dict[str, Any]:
        """Check for appointment conflicts for a doctor at a specific time."""
        if not DATABASE_AVAILABLE:
            return {"conflict": False, "message": "Database not available"}
        
        try:
            # Combine date and time into single datetime for comparison
            appt_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
            appt_time = datetime.strptime(appointment_time, "%H:%M").time()
            appt_datetime = datetime.combine(appt_date, appt_time)
            
            db = self.get_db_session()
            query = db.query(Appointment).filter(
                and_(
                    Appointment.doctor_id == uuid.UUID(doctor_id),
                    Appointment.appointment_date == appt_datetime,  # Use combined datetime
                    Appointment.status.in_(["scheduled", "confirmed"])
                )
            )
            
            # Exclude specific appointment if provided (for updates)
            if exclude_appointment_id:
                query = query.filter(Appointment.id != uuid.UUID(exclude_appointment_id))
            
            conflicting_appointment = query.first()
            db.close()
            
            if conflicting_appointment:
                return {
                    "conflict": True, 
                    "message": f"Doctor already has an appointment at {appointment_time} on {appointment_date}",
                    "conflicting_appointment_id": str(conflicting_appointment.id)
                }
            else:
                return {"conflict": False, "message": "No conflicts found"}
        except Exception as e:
            return {"conflict": True, "message": f"Error checking conflicts: {str(e)}"}

    def get_available_slots(self, doctor_id: str, date: str, duration_minutes: int = 30) -> Dict[str, Any]:
        """Get available time slots for a doctor on a specific date."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            from datetime import timedelta
            
            appt_date = datetime.strptime(date, "%Y-%m-%d").date()
            
            # Define working hours (9 AM to 5 PM)
            start_time = time(9, 0)
            end_time = time(17, 0)
            
            db = self.get_db_session()
            # Get existing appointments for the day
            existing_appointments = db.query(Appointment).filter(
                and_(
                    Appointment.doctor_id == uuid.UUID(doctor_id),
                    Appointment.appointment_date == appt_date,
                    Appointment.status.in_(["scheduled", "confirmed"])
                )
            ).order_by(Appointment.appointment_time).all()
            
            db.close()
            
            # Generate available slots
            available_slots = []
            current_time = datetime.combine(appt_date, start_time)
            end_datetime = datetime.combine(appt_date, end_time)
            slot_duration = timedelta(minutes=duration_minutes)
            
            while current_time + slot_duration <= end_datetime:
                slot_time = current_time.time()
                
                # Check if this slot conflicts with existing appointments
                is_available = True
                for appointment in existing_appointments:
                    if appointment.appointment_time == slot_time:
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append(slot_time.strftime("%H:%M"))
                
                current_time += slot_duration
            
            # Log the interaction
            self.log_interaction(
                query=f"Get available slots for doctor {doctor_id} on {date} (duration: {duration_minutes}min)",
                response=f"Found {len(available_slots)} available slots",
                tool_used="get_available_slots"
            )
            
            return {
                "data": available_slots,
                "date": date,
                "doctor_id": doctor_id,
                "duration_minutes": duration_minutes
            }
        except Exception as e:
            return {"error": f"Failed to get available slots: {str(e)}"}
