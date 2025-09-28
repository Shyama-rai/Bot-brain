# IMPORTANT: KEEP THIS COMMENT
# Using google-generativeai integration
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from typing import Dict, Any, Optional
import streamlit as st
import re
import os
from datetime import datetime
from difflib import SequenceMatcher

def get_string_similarity(s1: str, s2: str) -> float:
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

def normalize_location_name(name: str) -> str:
    """Normalize location name for better matching."""
    return re.sub(r'[^a-z0-9]', '', name.lower())

class GeminiAssistant:
    def __init__(self):
        """Initialize the Gemini AI assistant with campus knowledge."""
        # Initialize Gemini with secure API key from environment (if available)
        self.model = None
        
        if GENAI_AVAILABLE:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-pro')
                    print("Gemini API initialized successfully.")
                except Exception as e:
                    print(f"Warning: Could not initialize Gemini API: {e}")
            else:
                print("No GEMINI_API_KEY found. Running in local mode only.")
        else:
            print("Google Generative AI not available. Running in local mode only.")
        self.campus_info = {
            "flag_post": {
                "name": "Main Flag Post",
                "location": "Campus Entrance",
                "hours": "24/7",
                "facilities": ["Information Board", "Security Post"],
                "nearby": ["Entry Gate", "Exit Gate"],
                "description": "The central flag post marking the campus entrance"
            },
            "entry_gate": {
                "name": "Main Entry Gate",
                "location": "Campus Perimeter",
                "hours": "24/7",
                "facilities": ["Security Booth", "Visitor Registration", "Information Desk"],
                "nearby": ["Flag Post", "Check Post 1"],
                "description": "Primary entrance point with security checkpoints"
            },
            "exit_gate": {
                "name": "Exit Gate",
                "location": "Campus Perimeter",
                "hours": "24/7",
                "facilities": ["Security Booth", "Vehicle Check Point"],
                "nearby": ["Flag Post", "Check Post 2"],
                "description": "Main exit point from campus"
            },
            "check_post_1": {
                "name": "Check Post 1",
                "location": "North Campus",
                "hours": "24/7",
                "facilities": ["Security Check", "Visitor Registration"],
                "nearby": ["Entry Gate", "Acad 1"],
                "description": "Northern security checkpoint"
            },
            "check_post_2": {
                "name": "Check Post 2",
                "location": "South Campus",
                "hours": "24/7",
                "facilities": ["Security Check", "Information Desk"],
                "nearby": ["Exit Gate", "Acad 2"],
                "description": "Southern security checkpoint"
            },
            "acad_1": {
                "name": "Academic Block 1",
                "location": "Academic Zone",
                "hours": "7:00 AM - 6:00 PM",
                "facilities": ["Classrooms", "Labs", "Faculty Offices", "Seminar Halls"],
                "nearby": ["Library", "Faculty Block"],
                "description": "Primary academic building with modern facilities"
            },
            "acad_2": {
                "name": "Academic Block 2",
                "location": "Academic Zone",
                "hours": "7:00 AM - 6:00 PM",
                "facilities": ["Lecture Halls", "Computer Labs", "Study Areas"],
                "nearby": ["Library", "Food Court"],
                "description": "Secondary academic building focusing on specialized courses"
            },
            "library": {
                "name": "Central Library",
                "location": "Academic Zone",
                "hours": "8:00 AM - 10:00 PM",
                "facilities": ["Reading Rooms", "Digital Library", "Group Study Areas", "Research Section"],
                "nearby": ["Acad 1", "Acad 2"],
                "description": "Multi-story library with extensive collection and study spaces"
            },
            "food_court": {
                "name": "Campus Food Court",
                "location": "Student Zone",
                "hours": "7:30 AM - 9:00 PM",
                "facilities": ["Multiple Food Stalls", "Seating Area", "Vending Machines"],
                "nearby": ["Library", "Hostel Block"],
                "description": "Central dining facility with diverse food options"
            },
            "faculty_block": {
                "name": "Faculty Block",
                "location": "Academic Zone",
                "hours": "9:00 AM - 5:00 PM",
                "facilities": ["Faculty Offices", "Conference Rooms", "Meeting Areas"],
                "nearby": ["Acad 1", "Library"],
                "description": "Dedicated building for faculty offices and administrative work"
            },
            "hostel_block": {
                "name": "Student Hostel",
                "location": "Residential Zone",
                "hours": "24/7",
                "facilities": ["Dormitories", "Common Rooms", "Laundry", "Recreation Areas"],
                "nearby": ["Food Court", "Sports Facilities"],
                "description": "Student accommodation with modern amenities"
            },
            "cricket_ground": {
                "name": "Cricket Ground",
                "location": "Sports Zone",
                "hours": "6:00 AM - 7:00 PM",
                "facilities": ["Cricket Field", "Practice Nets", "Pavilion"],
                "nearby": ["Football Ground", "Basketball Court"],
                "description": "Regulation-size cricket ground with practice facilities"
            },
            "basketball_court": {
                "name": "Basketball Court",
                "location": "Sports Zone",
                "hours": "6:00 AM - 7:00 PM",
                "facilities": ["Basketball Court", "Seating Area", "Floodlights"],
                "nearby": ["Volleyball Court", "Tennis Court"],
                "description": "Standard basketball court with spectator seating"
            },
            "volleyball_court": {
                "name": "Volleyball Court",
                "location": "Sports Zone",
                "hours": "6:00 AM - 7:00 PM",
                "facilities": ["Volleyball Court", "Practice Area"],
                "nearby": ["Basketball Court", "Tennis Court"],
                "description": "Regulation volleyball court with practice areas"
            },
            "tennis_court": {
                "name": "Tennis Court",
                "location": "Sports Zone",
                "hours": "6:00 AM - 7:00 PM",
                "facilities": ["Tennis Courts", "Practice Wall", "Equipment Room"],
                "nearby": ["Volleyball Court", "Basketball Court"],
                "description": "Professional tennis courts with practice facilities"
            },
            "football_ground": {
                "name": "Football Ground",
                "location": "Sports Zone",
                "hours": "6:00 AM - 7:00 PM",
                "facilities": ["Football Field", "Practice Area", "Changing Rooms"],
                "nearby": ["Cricket Ground", "Rest Area"],
                "description": "Full-size football field with training areas"
            },
            "rest_area": {
                "name": "Campus Rest Area",
                "location": "Central Campus",
                "hours": "24/7",
                "facilities": ["Benches", "Shade Areas", "Water Points", "Vending Machines"],
                "nearby": ["Food Court", "Sports Zone"],
                "description": "Outdoor relaxation areas spread across campus"
            }
        }
        
        # Enhanced navigation patterns
        self.navigation_patterns = [
            r'(?:how (?:do|can|to))?\s*(?:get|go|walk|reach)\s+(?:from\s+)?([\w\s]+)\s+to\s+([\w\s]+)',
            r'(?:show|find|give)\s+(?:me\s+)?(?:the\s+)?(?:route|path|way|directions?)\s+(?:from\s+)?([\w\s]+)\s+to\s+([\w\s]+)',
            r'directions?\s+(?:from\s+)?([\w\s]+)\s+to\s+([\w\s]+)'
        ]

    def get_response(self, query: str) -> Dict[str, Any]:
        """Process user query with enhanced NLP."""
        try:
            query_lower = query.lower()
            
            # Initialize response with context
            response = self._initialize_response()
            
            # Check conversation context
            context = self._get_conversation_context()
            
            # Extract locations using regex patterns
            locations = self._extract_locations(query_lower, context)
            
            # Determine query type and handle accordingly
            if self._is_navigation_query(query_lower):
                response.update(self._handle_navigation_query(query_lower, locations))
            elif locations:
                response.update(self._handle_location_query(locations[0], query_lower))
            else:
                response.update(self._handle_general_query(query_lower))
            
            # Update conversation context
            self._update_conversation_context(response)
            
            return response

        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return self._create_error_response(str(e))

    def _extract_locations(self, query: str, context: Dict) -> list:
        """Extract locations using enhanced fuzzy matching."""
        locations = []
        query_normalized = normalize_location_name(query)
        
        # Check for locations in navigation patterns
        for pattern in self.navigation_patterns:
            matches = re.search(pattern, query.lower())
            if matches:
                potential_locations = [loc.strip() for loc in matches.groups() if loc]
                for pot_loc in potential_locations:
                    best_match = self._find_best_matching_location(pot_loc)
                    if best_match:
                        locations.append(best_match)
        
        # If no locations found through patterns, try direct matching
        if not locations:
            # Try to find any location mentions with fuzzy matching
            words = query.lower().split()
            for word in words:
                best_match = self._find_best_matching_location(word)
                if best_match and best_match not in locations:
                    locations.append(best_match)
        
        # Handle contextual references
        if not locations and ('here' in query or 'there' in query):
            if context.get('last_location'):
                locations.append(context['last_location'])
        
        return locations

    def _find_best_matching_location(self, query_term: str, threshold: float = 0.6) -> Optional[str]:
        """Find best matching location using fuzzy matching."""
        best_match = None
        highest_score = threshold
        
        query_normalized = normalize_location_name(query_term)
        
        for loc_key, loc_info in self.campus_info.items():
            # Check original location key
            score = get_string_similarity(query_normalized, normalize_location_name(loc_key))
            if score > highest_score:
                highest_score = score
                best_match = loc_key
            
            # Check location name
            score = get_string_similarity(query_normalized, normalize_location_name(loc_info['name']))
            if score > highest_score:
                highest_score = score
                best_match = loc_key
            
            # Check common variations
            variations = [
                loc_key.replace('_', ' '),
                loc_info['name'].lower(),
                loc_key.replace('block', '').strip(),
                loc_key.replace('court', '').strip(),
                loc_key.replace('ground', '').strip()
            ]
            
            for variation in variations:
                score = get_string_similarity(query_normalized, normalize_location_name(variation))
                if score > highest_score:
                    highest_score = score
                    best_match = loc_key
        
        return best_match

    def _initialize_response(self) -> Dict[str, Any]:
        """Initialize response with metadata."""
        return {
            "text": "",
            "show_route": False,
            "start": None,
            "end": None,
            "locations": [],
            "timestamp": datetime.now().isoformat(),
            "query_understood": False
        }

    def _get_conversation_context(self) -> Dict[str, Any]:
        """Get conversation context from session state."""
        if 'conversation_context' not in st.session_state:
            st.session_state.conversation_context = {
                'last_location': None,
                'last_query_type': None,
                'conversation_history': []
            }
        return st.session_state.conversation_context

    def _update_conversation_context(self, response: Dict[str, Any]):
        """Update conversation context with current response."""
        context = self._get_conversation_context()
        if response['locations']:
            context['last_location'] = response['locations'][-1]
        context['conversation_history'].append({
            'timestamp': response['timestamp'],
            'query_understood': response['query_understood']
        })
        st.session_state.conversation_context = context

    def _is_navigation_query(self, query: str) -> bool:
        """Enhanced navigation query detection."""
        return any(re.search(pattern, query) for pattern in self.navigation_patterns)

    def _handle_navigation_query(self, query: str, locations: list) -> Dict[str, Any]:
        """Handle navigation queries with enhanced location matching."""
        if len(locations) >= 2:
            start_loc, end_loc = locations[0], locations[1]
            start_info = self.campus_info[start_loc]
            end_info = self.campus_info[end_loc]
            
            return {
                "text": f"""### 🗺️ Navigation Instructions
I'll help you get from {start_info['name']} to {end_info['name']}.

**Start Point:** {start_info['location']}
**Destination:** {end_info['location']}
**Notable Landmarks:** Near {', '.join(end_info['nearby'])}

*The route is now displayed on the map above* ⬆️

**Additional Information:**
- Destination Hours: {end_info['hours']}
- Available Facilities: {', '.join(end_info['facilities'])}""",
                "show_route": True,
                "start": start_loc,
                "end": end_loc,
                "locations": locations,
                "query_understood": True
            }
        
        return {
            "text": """### 🤔 Need More Information
Please specify both start and destination locations. For example:
- "How do I get from the library to the cafeteria?"
- "Show me the way from the entrance to the academic block"
""",
            "show_route": False,
            "locations": []
        }

    def _handle_location_query(self, location: str, query: str) -> Dict[str, Any]:
        """Handle queries about specific locations."""
        info = self.campus_info[location]
        
        if "hour" in query or "time" in query or "open" in query:
            response_text = f"""### ⏰ {info['name']} Hours
- **Operating Hours:** {info['hours']}
- **Location:** {info['location']}"""
        
        elif "facilities" in query or "available" in query:
            response_text = f"""### 🏢 {info['name']} Facilities
- **Available Facilities:**
{chr(10).join(['  • ' + f for f in info['facilities']])}
- **Location:** {info['location']}
- **Hours:** {info['hours']}"""
        
        else:
            response_text = f"""### 📍 {info['name']}
- **Description:** {info['description']}
- **Location:** {info['location']}
- **Hours:** {info['hours']}
- **Nearby:** {', '.join(info['nearby'])}
- **Facilities:** {', '.join(info['facilities'])}"""

        return {
            "text": response_text,
            "show_route": False,
            "locations": [location]
        }

    def _handle_general_query(self, query: str) -> Dict[str, Any]:
        """Handle general queries about campus."""
        return {
            "text": """### 🎓 Campus Navigation Help
I can help you with:
1. **Finding Routes:** Ask "How do I get from X to Y?"
2. **Location Info:** Ask "Tell me about the library"
3. **Facilities:** Ask "What facilities are in X?"
4. **Hours:** Ask "When is X open?"

**Available Locations:**
{}""".format('\n'.join([f"- {info['name']}" for info in self.campus_info.values()])),
            "show_route": False,
            "locations": []
        }

    def _create_error_response(self, error: str) -> Dict[str, Any]:
        """Create a helpful error response."""
        return {
            "text": f"""### ❌ I encountered an issue
I apologize, but I had trouble processing your request. 
Try asking in a different way, for example:
- "How do I get to the library?"
- "What facilities are in the cafeteria?"
- "Show me the way from entrance to academic block"

Technical details: {error}""",
            "show_route": False,
            "start": None,
            "end": None,
            "locations": [],
            "query_understood": False
        }