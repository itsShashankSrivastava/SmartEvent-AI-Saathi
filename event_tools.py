"""
Event Planning Tools for LLM Function Calling
Provides decorated functions that the LLM can call to search venues, vendors, and estimate budgets
"""

import json
from typing import Dict, List, Optional, Any
from functools import wraps
import sys
import os

# Add parent directory to path to import event_search
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from event_search import search_engine
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False
    print("⚠️ Event search system not available")

# Function registry for LLM tools
AVAILABLE_FUNCTIONS = {}

def llm_tool(name: str, description: str, parameters: Dict[str, Any]):
    """
    Decorator to register functions as LLM tools
    
    Args:
        name: Function name for LLM to call
        description: Description of what the function does
        parameters: JSON schema describing the function parameters
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Register function with metadata
        AVAILABLE_FUNCTIONS[name] = {
            "function": wrapper,
            "description": description,
            "parameters": parameters
        }
        
        return wrapper
    return decorator

@llm_tool(
    name="search_venues",
    description="Search for event venues based on location, capacity, budget, and event type",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name (e.g., delhi, mumbai, bangalore)",
                "enum": ["delhi", "mumbai", "bangalore", "chennai", "hyderabad", "pune", "kolkata", "gurgaon", "noida", "kanpur", "ahmedabad"]
            },
            "area": {
                "type": "string", 
                "description": "Specific area within the city (optional)"
            },
            "capacity": {
                "type": "integer",
                "description": "Minimum number of people the venue should accommodate"
            },
            "budget_max": {
                "type": "integer",
                "description": "Maximum budget in rupees"
            },
            "event_type": {
                "type": "string",
                "description": "Type of event",
                "enum": ["wedding", "corporate", "birthday", "anniversary", "engagement", "reception"]
            }
        },
        "required": []
    }
)
def search_venues(city: Optional[str] = None, area: Optional[str] = None, 
                 capacity: Optional[int] = None, budget_max: Optional[int] = None, 
                 event_type: Optional[str] = None) -> Dict:
    """Search for venues matching the criteria"""
    if not SEARCH_AVAILABLE:
        return {"error": "Search system not available"}
    
    try:
        results = search_engine.search_venues(
            city=city,
            area=area, 
            capacity=capacity,
            budget_max=budget_max,
            event_type=event_type
        )
        
        # Format results for LLM
        formatted_results = []
        for venue in results[:5]:  # Top 5 results
            formatted_results.append({
                "name": venue["name"],
                "address": venue["address"],
                "city": venue["city"],
                "area": venue["area"],
                "capacity": venue["capacity"],
                "price_range": venue["price_range"],
                "rating": venue["rating"],
                "contact": venue["contact"],
                "amenities": venue.get("amenities", []),
                "suitable_for": venue.get("suitable_for", [])
            })
        
        return {
            "success": True,
            "total_found": len(results),
            "venues": formatted_results,
            "search_criteria": {
                "city": city,
                "area": area,
                "capacity": capacity,
                "budget_max": budget_max,
                "event_type": event_type
            }
        }
    except Exception as e:
        return {"error": f"Venue search failed: {str(e)}"}

@llm_tool(
    name="search_vendors",
    description="Search for event vendors like caterers, photographers, decorators, etc.",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name",
                "enum": ["delhi", "mumbai", "bangalore", "chennai", "hyderabad", "pune", "kolkata", "gurgaon", "noida", "kanpur", "ahmedabad"]
            },
            "vendor_type": {
                "type": "string",
                "description": "Type of vendor needed",
                "enum": ["flowers", "decoration", "food", "photography", "music_dj", "transportation", "makeup_artist", "tent_house"]
            },
            "budget_max": {
                "type": "integer",
                "description": "Maximum budget in rupees"
            },
            "speciality": {
                "type": "string",
                "description": "Vendor speciality (e.g., wedding, corporate, traditional)"
            }
        },
        "required": ["vendor_type"]
    }
)
def search_vendors(vendor_type: str, city: Optional[str] = None, 
                  budget_max: Optional[int] = None, speciality: Optional[str] = None) -> Dict:
    """Search for vendors matching the criteria"""
    if not SEARCH_AVAILABLE:
        return {"error": "Search system not available"}
    
    try:
        results = search_engine.search_vendors(
            city=city,
            vendor_type=vendor_type,
            budget_max=budget_max,
            speciality=speciality
        )
        
        # Format results for LLM
        formatted_results = []
        for vendor in results[:5]:  # Top 5 results
            formatted_results.append({
                "name": vendor["name"],
                "speciality": vendor["speciality"],
                "city": vendor["city"],
                "area": vendor["area"],
                "price_range": vendor["price_range"],
                "rating": vendor["rating"],
                "contact": vendor["contact"],
                "services": vendor.get("services", []),
                "experience_years": vendor.get("experience_years", 0)
            })
        
        return {
            "success": True,
            "total_found": len(results),
            "vendor_type": vendor_type,
            "vendors": formatted_results,
            "search_criteria": {
                "city": city,
                "vendor_type": vendor_type,
                "budget_max": budget_max,
                "speciality": speciality
            }
        }
    except Exception as e:
        return {"error": f"Vendor search failed: {str(e)}"}

@llm_tool(
    name="estimate_budget",
    description="Calculate detailed budget estimate for an event",
    parameters={
        "type": "object",
        "properties": {
            "event_type": {
                "type": "string",
                "description": "Type of event",
                "enum": ["wedding", "corporate", "birthday", "anniversary", "engagement"]
            },
            "guest_count": {
                "type": "integer",
                "description": "Number of guests/attendees",
                "minimum": 1
            },
            "city": {
                "type": "string",
                "description": "City where event will be held",
                "enum": ["delhi", "mumbai", "bangalore", "chennai", "hyderabad", "pune", "kolkata", "gurgaon", "noida", "kanpur", "ahmedabad"]
            },
            "budget_level": {
                "type": "string",
                "description": "Budget level preference",
                "enum": ["low", "medium", "high"],
                "default": "medium"
            }
        },
        "required": ["event_type", "guest_count"]
    }
)
def estimate_budget(event_type: str, guest_count: int, city: Optional[str] = None, 
                   budget_level: str = "medium") -> Dict:
    """Generate detailed budget estimate for an event"""
    if not SEARCH_AVAILABLE:
        return {"error": "Search system not available"}
    
    try:
        preferences = {"budget_level": budget_level}
        result = search_engine.get_budget_estimate(
            event_type=event_type,
            guest_count=guest_count,
            city=city,
            preferences=preferences
        )
        
        return {
            "success": True,
            "event_type": result["event_type"],
            "guest_count": result["guest_count"],
            "city": result["city"],
            "budget_level": result["budget_level"],
            "total_estimate": result["total_estimate"],
            "per_person_cost": result["per_person_average"],
            "breakdown": result["breakdown"],
            "subtotal": result["subtotal"],
            "contingency": result["contingency"]
        }
    except Exception as e:
        return {"error": f"Budget estimation failed: {str(e)}"}

@llm_tool(
    name="get_recommendations",
    description="Get intelligent recommendations based on natural language query",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language query describing event needs"
            },
            "city": {
                "type": "string",
                "description": "Preferred city",
                "enum": ["delhi", "mumbai", "bangalore", "chennai", "hyderabad", "pune", "kolkata", "gurgaon", "noida", "kanpur", "ahmedabad"]
            },
            "budget": {
                "type": "integer",
                "description": "Budget limit in rupees"
            },
            "guest_count": {
                "type": "integer",
                "description": "Number of guests"
            }
        },
        "required": ["query"]
    }
)
def get_recommendations(query: str, city: Optional[str] = None, 
                       budget: Optional[int] = None, guest_count: Optional[int] = None) -> Dict:
    """Get comprehensive recommendations based on natural language query"""
    if not SEARCH_AVAILABLE:
        return {"error": "Search system not available"}
    
    try:
        result = search_engine.get_recommendations(
            query=query,
            city=city,
            budget=budget,
            guest_count=guest_count
        )
        
        return {
            "success": True,
            "query": result["query"],
            "detected_event_type": result.get("detected_event_type"),
            "capacity": result.get("capacity"),
            "venues": result.get("venues", [])[:3],  # Top 3 venues
            "vendors": {k: v[:2] for k, v in result.get("vendors", {}).items()},  # Top 2 per vendor type
            "budget_estimate": result.get("budget_estimate"),
            "total_results": result.get("total_results", 0)
        }
    except Exception as e:
        return {"error": f"Recommendations failed: {str(e)}"}

@llm_tool(
    name="get_cities_and_areas",
    description="Get list of available cities and areas for event planning",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Specific city to get areas for (optional)"
            }
        },
        "required": []
    }
)
def get_cities_and_areas(city: Optional[str] = None) -> Dict:
    """Get available cities and areas"""
    if not SEARCH_AVAILABLE:
        return {"error": "Search system not available"}
    
    try:
        if city:
            areas = search_engine.get_city_areas(city)
            return {
                "success": True,
                "city": city,
                "areas": areas,
                "total_areas": len(areas)
            }
        else:
            cities = search_engine.get_all_cities()
            return {
                "success": True,
                "cities": cities,
                "total_cities": len(cities)
            }
    except Exception as e:
        return {"error": f"Failed to get location data: {str(e)}"}

def get_function_definitions() -> List[Dict]:
    """Get OpenAI-compatible function definitions for all registered tools"""
    functions = []
    
    for name, metadata in AVAILABLE_FUNCTIONS.items():
        functions.append({
            "type": "function",
            "function": {
                "name": name,
                "description": metadata["description"],
                "parameters": metadata["parameters"]
            }
        })
    
    return functions

def call_function(function_name: str, arguments: Dict[str, Any]) -> Dict:
    """Call a registered function with the given arguments"""
    if function_name not in AVAILABLE_FUNCTIONS:
        return {"error": f"Function '{function_name}' not found"}
    
    try:
        func = AVAILABLE_FUNCTIONS[function_name]["function"]
        result = func(**arguments)
        return result
    except Exception as e:
        return {"error": f"Function call failed: {str(e)}"}

# Export the main functions for use
__all__ = [
    'get_function_definitions',
    'call_function', 
    'AVAILABLE_FUNCTIONS',
    'search_venues',
    'search_vendors', 
    'estimate_budget',
    'get_recommendations',
    'get_cities_and_areas'
]