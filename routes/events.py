from fastapi import APIRouter, HTTPException
from typing import List, Optional
from class_types.agora_types import EventDetails
import json
import os
from datetime import datetime
import uuid

router = APIRouter(prefix="/events", tags=["events"])

# Simple in-memory storage (in production, use a proper database)
events_db = {}

@router.post("/create", response_model=EventDetails)
async def create_event(
    event_type: str,
    attendee_count: int,
    budget_range: str,
    preferred_date: str,
    location: str,
    special_requirements: Optional[str] = None
):
    """Create a new event"""
    try:
        event_id = str(uuid.uuid4())
        event = EventDetails(
            event_id=event_id,
            event_type=event_type,
            attendee_count=attendee_count,
            budget_range=budget_range,
            preferred_date=preferred_date,
            location=location,
            status="planning",
            rsvp_count=0,
            created_at=datetime.now().isoformat()
        )
        
        events_db[event_id] = event.dict()
        return event
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@router.get("/list", response_model=List[EventDetails])
async def list_events():
    """Get all events"""
    try:
        return [EventDetails(**event) for event in events_db.values()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events: {str(e)}")

@router.get("/{event_id}", response_model=EventDetails)
async def get_event(event_id: str):
    """Get specific event details"""
    try:
        if event_id not in events_db:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return EventDetails(**events_db[event_id])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve event: {str(e)}")

@router.put("/{event_id}/rsvp")
async def update_rsvp(event_id: str, attending: bool):
    """Update RSVP for an event"""
    try:
        if event_id not in events_db:
            raise HTTPException(status_code=404, detail="Event not found")
        
        event = events_db[event_id]
        if attending:
            event["rsvp_count"] += 1
        else:
            event["rsvp_count"] = max(0, event["rsvp_count"] - 1)
        
        return {"message": "RSVP updated successfully", "rsvp_count": event["rsvp_count"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update RSVP: {str(e)}")

@router.put("/{event_id}/status")
async def update_event_status(event_id: str, status: str):
    """Update event status"""
    try:
        if event_id not in events_db:
            raise HTTPException(status_code=404, detail="Event not found")
        
        valid_statuses = ["planning", "confirmed", "in_progress", "completed", "cancelled"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        events_db[event_id]["status"] = status
        return {"message": "Event status updated successfully", "status": status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update event status: {str(e)}")

@router.delete("/{event_id}")
async def delete_event(event_id: str):
    """Delete an event"""
    try:
        if event_id not in events_db:
            raise HTTPException(status_code=404, detail="Event not found")
        
        del events_db[event_id]
        return {"message": "Event deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")

@router.get("/venues/suggestions")
async def get_venue_suggestions(
    event_type: str,
    attendee_count: int,
    budget_range: str,
    location: Optional[str] = None
):
    """Get venue suggestions based on event requirements"""
    try:
        # Sample venue suggestions (in production, integrate with venue APIs)
        venue_suggestions = {
            "birthday_party": [
                {"name": "Community Center Hall", "capacity": 100, "price_range": "$200-500", "amenities": ["Kitchen", "Sound System", "Parking"]},
                {"name": "Local Restaurant Private Room", "capacity": 50, "price_range": "$300-800", "amenities": ["Catering", "Service Staff", "Decorations"]},
                {"name": "Park Pavilion", "capacity": 75, "price_range": "$100-300", "amenities": ["Outdoor Space", "BBQ Grills", "Playground"]}
            ],
            "corporate_event": [
                {"name": "Business Hotel Conference Room", "capacity": 200, "price_range": "$500-1500", "amenities": ["AV Equipment", "Catering", "Parking", "WiFi"]},
                {"name": "Co-working Event Space", "capacity": 100, "price_range": "$300-800", "amenities": ["Modern Tech", "Flexible Layout", "Catering Options"]},
                {"name": "Convention Center", "capacity": 500, "price_range": "$1000-3000", "amenities": ["Large Space", "Full Service", "Exhibition Areas"]}
            ],
            "wedding": [
                {"name": "Garden Venue", "capacity": 150, "price_range": "$2000-5000", "amenities": ["Outdoor Ceremony", "Reception Hall", "Bridal Suite", "Catering"]},
                {"name": "Banquet Hall", "capacity": 200, "price_range": "$1500-4000", "amenities": ["Full Service", "Dance Floor", "Bar Service", "Parking"]},
                {"name": "Beach Resort", "capacity": 100, "price_range": "$3000-8000", "amenities": ["Scenic Views", "All-Inclusive", "Photography", "Accommodation"]}
            ],
            "family_gathering": [
                {"name": "Community Park", "capacity": 50, "price_range": "$50-200", "amenities": ["Picnic Tables", "Playground", "BBQ Area", "Free Parking"]},
                {"name": "Family Restaurant", "capacity": 40, "price_range": "$200-600", "amenities": ["Private Dining", "Kid-Friendly", "Catering", "Easy Access"]},
                {"name": "Recreation Center", "capacity": 80, "price_range": "$150-400", "amenities": ["Indoor/Outdoor", "Activities", "Kitchen", "Parking"]}
            ]
        }
        
        # Get suggestions based on event type
        suggestions = venue_suggestions.get(event_type.lower().replace(" ", "_"), [])
        
        # Filter by capacity and budget if needed
        filtered_suggestions = []
        for venue in suggestions:
            if venue["capacity"] >= attendee_count:
                filtered_suggestions.append(venue)
        
        return {
            "event_type": event_type,
            "attendee_count": attendee_count,
            "budget_range": budget_range,
            "location": location,
            "suggestions": filtered_suggestions[:5]  # Return top 5 suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get venue suggestions: {str(e)}")

@router.get("/budget/estimate")
async def get_budget_estimate(
    event_type: str,
    attendee_count: int,
    venue_type: Optional[str] = None,
    catering_level: Optional[str] = "standard"
):
    """Get budget estimate for an event"""
    try:
        # Sample budget calculations (in production, use real pricing data)
        base_costs = {
            "birthday_party": {"venue": 15, "catering": 25, "entertainment": 10, "decorations": 8},
            "corporate_event": {"venue": 25, "catering": 40, "entertainment": 15, "av_equipment": 12},
            "wedding": {"venue": 50, "catering": 75, "entertainment": 30, "decorations": 25, "photography": 20},
            "family_gathering": {"venue": 10, "catering": 20, "entertainment": 5, "decorations": 5}
        }
        
        costs = base_costs.get(event_type.lower().replace(" ", "_"), base_costs["birthday_party"])
        
        # Calculate total per person
        total_per_person = sum(costs.values())
        
        # Apply multipliers based on options
        if catering_level == "premium":
            total_per_person *= 1.5
        elif catering_level == "budget":
            total_per_person *= 0.7
        
        total_estimate = total_per_person * attendee_count
        
        # Add contingency (15%)
        contingency = total_estimate * 0.15
        final_estimate = total_estimate + contingency
        
        breakdown = {
            "per_person_cost": round(total_per_person, 2),
            "base_total": round(total_estimate, 2),
            "contingency": round(contingency, 2),
            "final_estimate": round(final_estimate, 2),
            "cost_breakdown": {k: round(v * attendee_count, 2) for k, v in costs.items()}
        }
        
        return breakdown
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate budget estimate: {str(e)}")