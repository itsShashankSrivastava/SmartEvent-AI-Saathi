"""
Event Search and Recommendation System
Provides intelligent search and recommendations for venues and vendors
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path

class EventSearchEngine:
    def __init__(self, data_file: str = "event_data.json"):
        """Initialize the search engine with event data"""
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load event data from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Event data file {self.data_file} not found")
            return {"cities": {}}
    
    def search_venues(self, 
                     city: str = None, 
                     area: str = None, 
                     capacity: int = None, 
                     budget_min: int = None, 
                     budget_max: int = None,
                     event_type: str = None) -> List[Dict]:
        """
        Search for venues based on criteria
        
        Args:
            city: City name (e.g., 'delhi', 'mumbai')
            area: Area name (e.g., 'connaught_place', 'bandra')
            capacity: Minimum capacity required
            budget_min: Minimum budget in rupees
            budget_max: Maximum budget in rupees
            event_type: Type of event (e.g., 'wedding', 'corporate')
        
        Returns:
            List of matching venues with details
        """
        results = []
        
        # Search through all cities or specific city
        cities_to_search = [city.lower()] if city else self.data["cities"].keys()
        
        for city_key in cities_to_search:
            if city_key not in self.data["cities"]:
                continue
                
            city_data = self.data["cities"][city_key]
            
            # Search through all areas or specific area
            areas_to_search = [area.lower()] if area else city_data["areas"].keys()
            
            for area_key in areas_to_search:
                if area_key not in city_data["areas"]:
                    continue
                    
                area_data = city_data["areas"][area_key]
                
                for venue in area_data.get("venues", []):
                    # Check capacity
                    if capacity and venue.get("capacity", 0) < capacity:
                        continue
                    
                    # Check budget
                    venue_price = self._extract_price_range(venue.get("price_range", ""))
                    if budget_min and venue_price[1] < budget_min:
                        continue
                    if budget_max and venue_price[0] > budget_max:
                        continue
                    
                    # Check event type
                    if event_type and event_type.lower() not in venue.get("suitable_for", []):
                        continue
                    
                    # Add location info to venue
                    venue_result = venue.copy()
                    venue_result["city"] = city_data["name"]
                    venue_result["area"] = area_data["name"]
                    venue_result["city_key"] = city_key
                    venue_result["area_key"] = area_key
                    
                    results.append(venue_result)
        
        # Sort by rating (highest first)
        results.sort(key=lambda x: x.get("rating", 0), reverse=True)
        return results
    
    def search_vendors(self, 
                      city: str = None, 
                      area: str = None,
                      vendor_type: str = None, 
                      budget_min: int = None, 
                      budget_max: int = None,
                      speciality: str = None) -> List[Dict]:
        """
        Search for vendors based on criteria
        
        Args:
            city: City name
            area: Area name
            vendor_type: Type of vendor (e.g., 'flowers', 'food', 'music_dj')
            budget_min: Minimum budget in rupees
            budget_max: Maximum budget in rupees
            speciality: Vendor speciality (e.g., 'wedding', 'corporate')
        
        Returns:
            List of matching vendors with details
        """
        results = []
        
        # Search through all cities or specific city
        cities_to_search = [city.lower()] if city else self.data["cities"].keys()
        
        for city_key in cities_to_search:
            if city_key not in self.data["cities"]:
                continue
                
            city_data = self.data["cities"][city_key]
            
            # Search through all areas or specific area
            areas_to_search = [area.lower()] if area else city_data["areas"].keys()
            
            for area_key in areas_to_search:
                if area_key not in city_data["areas"]:
                    continue
                    
                area_data = city_data["areas"][area_key]
                vendors_data = area_data.get("vendors", {})
                
                # Search through all vendor types or specific type
                vendor_types_to_search = [vendor_type] if vendor_type else vendors_data.keys()
                
                for vtype in vendor_types_to_search:
                    if vtype not in vendors_data:
                        continue
                    
                    for vendor in vendors_data[vtype]:
                        # Check budget
                        vendor_price = self._extract_price_range(vendor.get("price_range", ""))
                        if budget_min and vendor_price[1] < budget_min:
                            continue
                        if budget_max and vendor_price[0] > budget_max:
                            continue
                        
                        # Check speciality
                        if speciality and speciality.lower() not in vendor.get("speciality", "").lower():
                            continue
                        
                        # Add location and type info to vendor
                        vendor_result = vendor.copy()
                        vendor_result["city"] = city_data["name"]
                        vendor_result["area"] = area_data["name"]
                        vendor_result["city_key"] = city_key
                        vendor_result["area_key"] = area_key
                        vendor_result["vendor_type"] = vtype
                        
                        results.append(vendor_result)
        
        # Sort by rating (highest first)
        results.sort(key=lambda x: x.get("rating", 0), reverse=True)
        return results
    
    def get_budget_estimate(self, 
                           event_type: str, 
                           guest_count: int, 
                           city: str = None,
                           preferences: Dict = None) -> Dict:
        """
        Generate budget estimate for an event
        
        Args:
            event_type: Type of event
            guest_count: Number of guests
            city: City for the event
            preferences: User preferences (budget_level, etc.)
        
        Returns:
            Detailed budget breakdown
        """
        preferences = preferences or {}
        budget_level = preferences.get("budget_level", "medium")  # low, medium, high
        
        # Base cost per person based on city and budget level
        city_multipliers = {
            "mumbai": 1.4,
            "delhi": 1.3,
            "bangalore": 1.2,
            "hyderabad": 1.1,
            "chennai": 1.0,
            "pune": 1.0,
            "gurgaon": 1.3,
            "noida": 1.1,
            "kolkata": 0.9,
            "kanpur": 0.8,
            "ahmedabad": 0.9
        }
        
        budget_multipliers = {
            "low": 0.6,
            "medium": 1.0,
            "high": 1.8
        }
        
        # Base costs per person
        base_costs = {
            "wedding": {
                "venue": 800,
                "food": 600,
                "decoration": 400,
                "flowers": 200,
                "photography": 300,
                "music_dj": 150,
                "transportation": 100
            },
            "corporate": {
                "venue": 500,
                "food": 400,
                "decoration": 200,
                "flowers": 100,
                "photography": 200,
                "music_dj": 100,
                "transportation": 80
            },
            "birthday": {
                "venue": 300,
                "food": 350,
                "decoration": 250,
                "flowers": 100,
                "photography": 150,
                "music_dj": 100,
                "transportation": 50
            }
        }
        
        # Get base costs for event type
        event_costs = base_costs.get(event_type, base_costs["birthday"])
        
        # Apply multipliers
        city_mult = city_multipliers.get(city.lower() if city else "delhi", 1.0)
        budget_mult = budget_multipliers.get(budget_level, 1.0)
        
        # Calculate costs
        breakdown = {}
        total_cost = 0
        
        for category, base_cost in event_costs.items():
            category_cost = base_cost * guest_count * city_mult * budget_mult
            breakdown[category] = {
                "cost": round(category_cost),
                "per_person": round(base_cost * city_mult * budget_mult)
            }
            total_cost += category_cost
        
        # Add contingency (15%)
        contingency = total_cost * 0.15
        final_total = total_cost + contingency
        
        return {
            "event_type": event_type,
            "guest_count": guest_count,
            "city": city,
            "budget_level": budget_level,
            "breakdown": breakdown,
            "subtotal": round(total_cost),
            "contingency": round(contingency),
            "total_estimate": round(final_total),
            "per_person_average": round(final_total / guest_count)
        }
    
    def get_recommendations(self, 
                           query: str, 
                           city: str = None, 
                           budget: int = None,
                           guest_count: int = None) -> Dict:
        """
        Get intelligent recommendations based on natural language query
        
        Args:
            query: Natural language query (e.g., "wedding venue in delhi for 200 people")
            city: City preference
            budget: Budget limit
            guest_count: Number of guests
        
        Returns:
            Comprehensive recommendations
        """
        # Parse query for keywords
        query_lower = query.lower()
        
        # Detect event type
        event_types = ["wedding", "corporate", "birthday", "anniversary", "engagement", 
                      "reception", "conference", "seminar", "party"]
        detected_event = None
        for event_type in event_types:
            if event_type in query_lower:
                detected_event = event_type
                break
        
        # Detect vendor types
        vendor_keywords = {
            "flowers": ["flower", "floral", "bouquet", "decoration"],
            "food": ["food", "catering", "caterer", "cuisine", "meal"],
            "music_dj": ["music", "dj", "band", "entertainment"],
            "photography": ["photo", "photographer", "videography"],
            "transportation": ["car", "transport", "vehicle", "cab"],
            "decoration": ["decor", "decoration", "theme"]
        }
        
        detected_vendors = []
        for vendor_type, keywords in vendor_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_vendors.append(vendor_type)
        
        # Extract numbers (for capacity/budget)
        numbers = re.findall(r'\d+', query)
        
        # Determine capacity from query or parameter
        capacity = guest_count
        if not capacity and numbers:
            # Look for capacity indicators
            for i, num in enumerate(numbers):
                num_val = int(num)
                if 10 <= num_val <= 2000:  # Reasonable capacity range
                    capacity = num_val
                    break
        
        # Search for venues
        venues = []
        if "venue" in query_lower or "hall" in query_lower or detected_event:
            venues = self.search_venues(
                city=city,
                capacity=capacity,
                budget_max=budget,
                event_type=detected_event
            )[:5]  # Top 5 venues
        
        # Search for vendors
        vendors = {}
        if detected_vendors or "vendor" in query_lower:
            vendor_types_to_search = detected_vendors if detected_vendors else ["flowers", "food", "music_dj", "photography"]
            
            for vendor_type in vendor_types_to_search:
                vendor_results = self.search_vendors(
                    city=city,
                    vendor_type=vendor_type,
                    budget_max=budget
                )[:3]  # Top 3 per category
                
                if vendor_results:
                    vendors[vendor_type] = vendor_results
        
        # Generate budget estimate
        budget_estimate = None
        if detected_event and capacity:
            budget_estimate = self.get_budget_estimate(
                event_type=detected_event,
                guest_count=capacity,
                city=city
            )
        
        return {
            "query": query,
            "detected_event_type": detected_event,
            "detected_vendors": detected_vendors,
            "capacity": capacity,
            "venues": venues,
            "vendors": vendors,
            "budget_estimate": budget_estimate,
            "total_results": len(venues) + sum(len(v) for v in vendors.values())
        }
    
    def _extract_price_range(self, price_str: str) -> Tuple[int, int]:
        """Extract min and max price from price range string"""
        if not price_str:
            return (0, 0)
        
        # Remove currency symbols and commas
        clean_str = re.sub(r'[₹,]', '', price_str)
        
        # Find numbers
        numbers = re.findall(r'\d+', clean_str)
        
        if len(numbers) >= 2:
            return (int(numbers[0]), int(numbers[1]))
        elif len(numbers) == 1:
            num = int(numbers[0])
            return (num, num)
        else:
            return (0, 0)
    
    def get_city_areas(self, city: str) -> List[str]:
        """Get all areas in a city"""
        city_key = city.lower()
        if city_key in self.data["cities"]:
            return list(self.data["cities"][city_key]["areas"].keys())
        return []
    
    def get_all_cities(self) -> List[str]:
        """Get all available cities"""
        return [city_data["name"] for city_data in self.data["cities"].values()]
    
    def get_vendor_categories(self) -> List[str]:
        """Get all available vendor categories"""
        return self.data.get("vendor_categories", [])

# Initialize global search engine instance
search_engine = EventSearchEngine()

def search_venues_api(city: str = None, area: str = None, capacity: int = None, 
                     budget_min: int = None, budget_max: int = None, event_type: str = None):
    """API wrapper for venue search"""
    return search_engine.search_venues(city, area, capacity, budget_min, budget_max, event_type)

def search_vendors_api(city: str = None, area: str = None, vendor_type: str = None,
                      budget_min: int = None, budget_max: int = None, speciality: str = None):
    """API wrapper for vendor search"""
    return search_engine.search_vendors(city, area, vendor_type, budget_min, budget_max, speciality)

def get_recommendations_api(query: str, city: str = None, budget: int = None, guest_count: int = None):
    """API wrapper for intelligent recommendations"""
    return search_engine.get_recommendations(query, city, budget, guest_count)

def get_budget_estimate_api(event_type: str, guest_count: int, city: str = None, preferences: Dict = None):
    """API wrapper for budget estimation"""
    return search_engine.get_budget_estimate(event_type, guest_count, city, preferences)