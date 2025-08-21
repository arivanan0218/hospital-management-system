"""Room & Bed Management Agent - Handles room and bed operations"""

import uuid
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from .base_agent import BaseAgent

try:
    from database import Room, Bed, Patient, Department, SessionLocal
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


class RoomBedAgent(BaseAgent):
    """Agent specialized in room and bed management operations"""
    
    def __init__(self):
        super().__init__("Room & Bed Management Agent", "room_bed_agent")
    
    def get_tools(self) -> List[str]:
        """Return list of room and bed management tools"""
        return [
            "create_room",
            "list_rooms",
            "get_room_by_id",
            "update_room",
            "delete_room",
            "create_bed",
            "list_beds",
            "get_bed_by_id",
            "get_bed_by_number",
            "assign_bed_to_patient",
            "discharge_bed",
            "update_bed_status"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Return list of room and bed management capabilities"""
        return [
            "Room allocation and management",
            "Bed inventory tracking",
            "Patient bed assignments",
            "Bed occupancy monitoring",
            "Room and bed availability checking",
            "Patient admission and discharge"
        ]
    
    # ROOM MANAGEMENT METHODS
    
    def create_room(self, room_number: str, department_id: str, room_type: str = None,
                   floor_number: int = None, capacity: int = None) -> Dict[str, Any]:
        """Create a new room."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            db = self.get_db_session()
            room = Room(
                room_number=room_number,
                department_id=uuid.UUID(department_id),
                room_type=room_type,
                floor_number=floor_number,
                capacity=capacity
            )
            db.add(room)
            db.commit()
            db.refresh(room)
            result = self.serialize_model(room)
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Create room: {room_number}",
                response=f"Room created successfully with ID: {result['id']}",
                tool_used="create_room"
            )
            
            return {"success": True, "message": "Room created successfully", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to create room: {str(e)}"}

    def list_rooms(self, department_id: str = None, status: str = None) -> Dict[str, Any]:
        """List rooms with optional filtering - brief information only."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            db = self.get_db_session()
            query = db.query(Room)
            
            filters = []
            if department_id:
                query = query.filter(Room.department_id == uuid.UUID(department_id))
                filters.append(f"department_id: {department_id}")
            
            if status:
                query = query.filter(Room.status == status)
                filters.append(f"status: {status}")
            
            rooms = query.all()
            
            # Return only essential information for list views
            result = []
            for room in rooms:
                brief_info = {
                    "id": str(room.id),
                    "room_number": room.room_number,
                    "room_type": room.room_type,
                    "department_id": str(room.department_id) if room.department_id else None,
                    "capacity": room.capacity,
                    "status": room.status
                }
                result.append(brief_info)
            
            db.close()
            
            # Log the interaction
            filter_text = f" with filters: {', '.join(filters)}" if filters else ""
            self.log_interaction(
                query=f"List rooms{filter_text}",
                response=f"Found {len(result)} rooms",
                tool_used="list_rooms"
            )
            
            return {"data": result}
        except Exception as e:
            return {"error": f"Failed to list rooms: {str(e)}"}

    def get_room_by_id(self, room_id: str) -> Dict[str, Any]:
        """Get a room by ID."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            db = self.get_db_session()
            room = db.query(Room).filter(Room.id == uuid.UUID(room_id)).first()
            result = self.serialize_model(room) if room else None
            db.close()
            
            if result:
                # Log the interaction
                self.log_interaction(
                    query=f"Get room by ID: {room_id}",
                    response=f"Room found: {result.get('room_number', 'N/A')}",
                    tool_used="get_room_by_id"
                )
                return {"data": result}
            else:
                return {"error": "Room not found"}
        except Exception as e:
            return {"error": f"Failed to get room: {str(e)}"}

    def update_room(self, room_id: str, room_number: str = None, room_type: str = None,
                   capacity: int = None) -> Dict[str, Any]:
        """Update room information."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            db = self.get_db_session()
            room = db.query(Room).filter(Room.id == uuid.UUID(room_id)).first()
            
            if not room:
                db.close()
                return {"success": False, "message": "Room not found"}
            
            # Update provided fields
            update_fields = []
            if room_number is not None:
                room.room_number = room_number
                update_fields.append("room_number")
            if room_type is not None:
                room.room_type = room_type
                update_fields.append("room_type")
            if capacity is not None:
                room.capacity = capacity
                update_fields.append("capacity")
            
            db.commit()
            db.refresh(room)
            result = self.serialize_model(room)
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Update room {room_id}: {', '.join(update_fields)}",
                response=f"Room updated successfully",
                tool_used="update_room"
            )
            
            return {"success": True, "message": "Room updated successfully", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to update room: {str(e)}"}

    def delete_room(self, room_id: str) -> Dict[str, Any]:
        """Delete a room."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            db = self.get_db_session()
            room = db.query(Room).filter(Room.id == uuid.UUID(room_id)).first()
            
            if not room:
                db.close()
                return {"success": False, "message": "Room not found"}
            
            room_number = room.room_number  # Store for logging
            db.delete(room)
            db.commit()
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Delete room: {room_id}",
                response=f"Room {room_number} deleted successfully",
                tool_used="delete_room"
            )
            
            return {"success": True, "message": "Room deleted successfully"}
        except Exception as e:
            return {"success": False, "message": f"Failed to delete room: {str(e)}"}

    # BED MANAGEMENT METHODS
    
    def create_bed(self, bed_number: str, room_id: str, bed_type: str = None, 
                  status: str = "available") -> Dict[str, Any]:
        """Create a new bed."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            db = self.get_db_session()
            bed = Bed(
                bed_number=bed_number,
                room_id=uuid.UUID(room_id),
                bed_type=bed_type,
                status=status
            )
            db.add(bed)
            db.commit()
            db.refresh(bed)
            result = self.serialize_model(bed)
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Create bed: {bed_number}",
                response=f"Bed created successfully with ID: {result['id']}",
                tool_used="create_bed"
            )
            
            return {"success": True, "message": "Bed created successfully", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to create bed: {str(e)}"}

    def list_beds(self, status: str = None, room_id: str = None) -> Dict[str, Any]:
        """List beds with optional filtering."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            db = self.get_db_session()
            query = db.query(Bed)
            
            filters = []
            if status:
                query = query.filter(Bed.status == status)
                filters.append(f"status: {status}")
            if room_id:
                query = query.filter(Bed.room_id == uuid.UUID(room_id))
                filters.append(f"room_id: {room_id}")
            
            beds = query.all()
            
            # Return only essential information for list views
            result = []
            for bed in beds:
                brief_info = {
                    "id": str(bed.id),
                    "bed_number": bed.bed_number,
                    "room_id": str(bed.room_id) if bed.room_id else None,
                    "room_number": getattr(bed.room, 'room_number', None) if bed.room else None,
                    "status": bed.status,
                    "patient_id": str(bed.patient_id) if bed.patient_id else None,
                    "admission_date": bed.admission_date.isoformat() if bed.admission_date else None
                }
                result.append(brief_info)
            
            db.close()
            
            # Log the interaction
            filter_text = f" with filters: {', '.join(filters)}" if filters else ""
            self.log_interaction(
                query=f"List beds{filter_text}",
                response=f"Found {len(result)} beds",
                tool_used="list_beds"
            )
            
            return {"data": result}
        except Exception as e:
            return {"error": f"Failed to list beds: {str(e)}"}

    def get_bed_by_id(self, bed_id: str) -> Dict[str, Any]:
        """Get a bed by ID."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            db = self.get_db_session()
            bed = db.query(Bed).filter(Bed.id == uuid.UUID(bed_id)).first()
            result = self.serialize_model(bed) if bed else None
            db.close()
            
            if result:
                # Log the interaction
                self.log_interaction(
                    query=f"Get bed by ID: {bed_id}",
                    response=f"Bed found: {result.get('bed_number', 'N/A')}",
                    tool_used="get_bed_by_id"
                )
                return {"data": result}
            else:
                return {"error": "Bed not found"}
        except Exception as e:
            return {"error": f"Failed to get bed: {str(e)}"}

    def get_bed_by_number(self, bed_number: str) -> Dict[str, Any]:
        """Get a bed by bed number."""
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        try:
            db = self.get_db_session()
            bed = db.query(Bed).filter(Bed.bed_number == bed_number).first()
            result = self.serialize_model(bed) if bed else None
            db.close()
            
            if result:
                # Log the interaction
                self.log_interaction(
                    query=f"Get bed by number: {bed_number}",
                    response=f"Bed {bed_number} found with ID: {result.get('id', 'N/A')}",
                    tool_used="get_bed_by_number"
                )
                return {"data": result}
            else:
                return {"error": f"Bed not found with number: {bed_number}"}
        except Exception as e:
            return {"error": f"Failed to get bed by number: {str(e)}"}

    def assign_bed_to_patient(self, bed_id: str, patient_id: str, 
                             admission_date: str = None) -> Dict[str, Any]:
        """Assign a bed to a patient."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            db = self.get_db_session()
            bed = db.query(Bed).filter(Bed.id == uuid.UUID(bed_id)).first()
            patient = db.query(Patient).filter(Patient.id == uuid.UUID(patient_id)).first()
            
            if not bed:
                db.close()
                return {"success": False, "message": "Bed not found"}
            if not patient:
                db.close()
                return {"success": False, "message": "Patient not found"}
            if bed.status != "available":
                db.close()
                return {"success": False, "message": f"Bed is not available (current status: {bed.status})"}
            
            # Assign bed to patient
            bed.patient_id = uuid.UUID(patient_id)
            bed.status = "occupied"
            if admission_date:
                bed.admission_date = datetime.strptime(admission_date, "%Y-%m-%d").date()
            else:
                bed.admission_date = date.today()
            
            db.commit()
            db.refresh(bed)
            result = self.serialize_model(bed)
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Assign bed {bed_id} to patient {patient_id}",
                response=f"Bed {bed.bed_number} assigned to patient {patient.first_name} {patient.last_name}",
                tool_used="assign_bed_to_patient"
            )
            
            return {"success": True, "message": "Bed assigned successfully", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to assign bed: {str(e)}"}

    def discharge_bed(self, bed_id: str, discharge_date: str = None) -> Dict[str, Any]:
        """Discharge a patient from a bed."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            db = self.get_db_session()
            bed = db.query(Bed).filter(Bed.id == uuid.UUID(bed_id)).first()
            
            if not bed:
                db.close()
                return {"success": False, "message": "Bed not found"}
            if bed.status != "occupied":
                db.close()
                return {"success": False, "message": f"Bed is not occupied (current status: {bed.status})"}
            
            # Discharge patient from bed
            patient_id = bed.patient_id
            bed.patient_id = None
            bed.status = "available"
            if discharge_date:
                bed.discharge_date = datetime.strptime(discharge_date, "%Y-%m-%d").date()
            else:
                bed.discharge_date = date.today()
            
            db.commit()
            db.refresh(bed)
            result = self.serialize_model(bed)
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Discharge bed {bed_id}",
                response=f"Bed {bed.bed_number} discharged, patient {patient_id} released",
                tool_used="discharge_bed"
            )
            
            return {"success": True, "message": "Bed discharged successfully", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to discharge bed: {str(e)}"}

    def update_bed_status(self, bed_id: str, status: str, notes: str = None) -> Dict[str, Any]:
        """Update bed status (available, occupied, maintenance, out_of_service)."""
        if not DATABASE_AVAILABLE:
            return {"success": False, "message": "Database not available"}
        
        try:
            db = self.get_db_session()
            bed = db.query(Bed).filter(Bed.id == uuid.UUID(bed_id)).first()
            
            if not bed:
                db.close()
                return {"success": False, "message": "Bed not found"}
            
            old_status = bed.status
            bed.status = status
            if notes:
                bed.notes = notes
            
            db.commit()
            db.refresh(bed)
            result = self.serialize_model(bed)
            db.close()
            
            # Log the interaction
            self.log_interaction(
                query=f"Update bed {bed_id} status from {old_status} to {status}",
                response=f"Bed status updated successfully",
                tool_used="update_bed_status"
            )
            
            return {"success": True, "message": "Bed status updated successfully", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to update bed status: {str(e)}"}
