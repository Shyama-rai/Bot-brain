import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from pathfinding import CampusPathfinder
from gemini_integration import GeminiAssistant

# Load environment variables from .env file
try:
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
except FileNotFoundError:
    pass  # .env file is optional

# Page configuration
st.set_page_config(
    page_title="CyberNav: Campus Route AI",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- START OF MODIFIED CSS THEME (Dark Background, Light Text) ---
# Professional Dark Theme
st.markdown("""
<style>
    /* Global theme - Dark background, light text */
    .stApp {
        background-color: #1e1e1e; /* Dark background */
        color: #ffffff; /* White text */
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    /* Header styling - Dark background with light text */
    .main-header {
        background-color: #2d2d2d;
        border: 1px solid #404040; /* Darker border */
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3); /* Darker shadow */
    }
    
    .main-header h1 {
        color: #ffffff; /* White title */
        margin: 0;
        font-weight: 700;
        font-size: 2rem;
    }
    
    .main-header p {
        color: #cccccc; /* Light gray subtitle */
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #2d2d2d; /* Dark tab background */
        border-radius: 5px;
        border: 1px solid #404040;
        padding: 0.25rem;
        margin-bottom: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #ffffff;
        border-radius: 4px;
        font-weight: 500;
        font-size: 0.95rem;
        padding: 0.5rem 1rem;
        margin: 0 0.1rem;
        border: 1px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #404040;
        border-color: #555555;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #007bff !important; /* Professional primary blue for selected */
        color: #ffffff !important;
        border-color: #007bff !important;
        font-weight: 600;
    }
    
    /* Containers (Map, Info, AI) */
    .map-container, .info-panel, .ai-container {
        background-color: #2d2d2d;
        border: 1px solid #404040; /* Dark border */
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    .map-container h3, .info-panel h3, .ai-container h3 {
        color: #ffffff;
        margin-bottom: 1rem;
        font-weight: 600;
        border-bottom: 1px solid #404040;
        padding-bottom: 0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #007bff; /* Primary blue button */
        color: #ffffff;
        border: 1px solid #007bff;
        padding: 0.75rem 2rem;
        border-radius: 5px;
        font-weight: 600;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #0056b3; /* Darker blue on hover */
        border-color: #0056b3;
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #2d2d2d; /* Dark background */
        border: 1px solid #404040;
        padding: 1rem;
        border-radius: 5px;
    }
    
    div[data-testid="metric-container"] label {
        color: #cccccc !important; /* Light label */
        font-weight: 500;
    }
    
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        color: #ffffff !important; /* White value */
        font-weight: 700;
    }
    
    /* Select boxes & Input fields */
    .stSelectbox > div > div, .stTextInput > div > div > input, .stChatInput > div > div > input {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        color: #ffffff;
        border-radius: 5px;
    }
    
    .stSelectbox label {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Data tables */
    .stDataFrame {
        border-radius: 5px;
        overflow: hidden;
        border: 1px solid #404040;
        background-color: #2d2d2d;
        color: #ffffff;
    }
    
    /* Chat styling */
    .stChatMessage {
        background-color: #2d2d2d; /* Dark background for chat bubbles */
        border: 1px solid #404040;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #ffffff;
    }

    /* Override for the 'Select Neural Route' placeholder text */
    .info-panel h4, .info-panel p {
        color: #cccccc !important; /* Ensure placeholder text is visible */
    }
    
    /* Text colors */
    .stMarkdown, .stText, p, div {
        color: #ffffff;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
</style>
""", unsafe_allow_html=True)
# --- END OF MODIFIED CSS THEME ---

# Initialize pathfinder and Gemini assistant
@st.cache_resource
def initialize_pathfinder():
    return CampusPathfinder("attached_assets/map_1758707724808.osm")

@st.cache_resource
def initialize_gemini():
    try:
        # Check for API key in environment variables (set by Replit Secrets)
        if not os.environ.get("GEMINI_API_KEY"):
            st.warning("🔧 AI Assistant unavailable: GEMINI_API_KEY not configured")
            return None
        return GeminiAssistant()
    except Exception as e:
        st.error(f"Failed to initialize AI Assistant: {str(e)}")
        return None

try:
    pathfinder = initialize_pathfinder()
    gemini = initialize_gemini()
    
    # Professional Header (Updated content for clarity)
    st.markdown("""
    <div class="main-header">
        <h1>🗺️ CyberNav: Campus Route AI</h1>
        <p>Advanced pathfinding system with integrated AI assistance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for the new layout
    tab1, tab2 = st.tabs(["🗺️ Route Planner", "🧪 AI & Analysis"])
    
    # Tab 1: Route Planner
    with tab1:
        # Route planning controls (moved from sidebar)
        st.markdown("""
        <div class="map-container">
            <h3>🎯 Route Configuration</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col_control1, col_control2, col_control3 = st.columns(3)
        
        with col_control1:
            st.markdown("**Select Journey Points**")
            locations = list(pathfinder.POIS.keys())
            start_location = st.selectbox("🚀 Start Location", locations, index=0, help="Choose your starting point")
            
        with col_control2:
            end_location = st.selectbox("🎯 Destination", locations, index=1, help="Choose your destination")
            
        with col_control3:
            algorithm = st.selectbox(
                "⚡ Pathfinding Algorithm",
                ["A*", "A* (Euclidean)", "A* (Manhattan)", "A* (Combined)", "BFS", "DFS", "UCS"],
                index=0,
                help="Choose the pathfinding algorithm. A* variants are recommended for optimal routes."
            )
        
        # Find path button
        st.markdown("<br>", unsafe_allow_html=True)
        run_pathfinding = st.button("🔥 FIND OPTIMAL PATH", type="primary", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Map and route information side by side
        col1, col2 = st.columns([2.2, 1], gap="large")
        
        with col1:
            st.markdown("""
            <div class="map-container">
                <h3>🗺️ Interactive Map</h3>
            """, unsafe_allow_html=True)
            
            # Initialize map display
            if 'current_map' not in st.session_state:
                st.session_state['current_map'] = pathfinder.create_base_map()
            
            # Handle pathfinding request
            if run_pathfinding:
                try:
                    with st.spinner(f"Processing using {algorithm}..."):
                        result = pathfinder.find_path(start_location, end_location, algorithm)
                        st.session_state['current_map'] = result['map']
                        st.session_state['path_metrics'] = result['metrics']
                        st.session_state['algorithm_used'] = algorithm
                        
                    st.success(f"⚡ Optimal path calculated using {algorithm} algorithm!")
                except Exception as e:
                    st.error(f"🚨 Pathway error: {str(e)}")
            
            # Display map
            if st.session_state['current_map']:
                map_data = st_folium(
                    st.session_state['current_map'],
                    width=None,
                    height=500,
                    returned_objects=["last_clicked"]
                )
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-panel">
                <h3>📊 Route Data</h3>
            """, unsafe_allow_html=True)
            
            # Route metrics display
            if 'path_metrics' in st.session_state:
                metrics = st.session_state['path_metrics']
                algorithm_used = st.session_state.get('algorithm_used', 'Unknown')
                
                # Metrics in organized columns
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric("⚡ Algorithm", algorithm_used)
                    st.metric("📏 Distance", f"{metrics['distance']:.0f}m")
                with col_m2:
                    st.metric("⏱️ Time", f"{metrics['time']:.1f} min")
                    st.metric("🔍 Explored", f"{metrics['nodes_explored']:,}")
                
                # Route details
                st.markdown("---")
                st.markdown("**Journey Path**")
                
                start_info = pathfinder.get_location_info(metrics['start_location'])
                end_info = pathfinder.get_location_info(metrics['end_location'])
                
                st.markdown(f"""
**From:** {start_info['name']}  
**To:** {end_info['name']}  
**Status:** ✅ Optimal path found
                """)
            else:
                # Changed text color to a professional visible gray
                st.markdown("""
                <div style="padding: 2rem; text-align: center;">
                    <h4 style="color: #cccccc;">Select Route</h4>
                    <p style="color: #aaaaaa;">Configure start and destination, then activate 'FIND OPTIMAL PATH' to calculate route.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Tab 2: AI & Analysis
    with tab2:
        col_ai1, col_ai2 = st.columns([1, 1], gap="large")
        
        with col_ai1:
            # AI Chat Interface
            st.markdown("""
            <div class="ai-container">
                <h3>🤖 AI Campus Assistant</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Initialize chat history
            if 'messages' not in st.session_state:
                st.session_state.messages = []

            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat input with proper error handling
            if gemini is None:
                st.info("🔧 AI Assistant is currently offline. Please configure GEMINI_API_KEY to activate.")
                st.chat_input("AI Assistant offline...", disabled=True)
            else:
                user_query = st.chat_input("Query the campus network...")
                
                if user_query:
                    # Add user message to chat
                    st.session_state.messages.append({"role": "user", "content": user_query})
                    with st.chat_message("user"):
                        st.markdown(user_query)
                    
                    # Generate AI response
                    with st.chat_message("assistant"):
                        with st.spinner("🧠 Processing..."):
                            try:
                                # Get AI response
                                response = gemini.get_response(user_query)
                                
                                # Display the response
                                st.markdown(response["text"])
                                
                                # Add assistant response to chat history
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": response["text"]
                                })
                                
                            except Exception as e:
                                st.error("🚨 Network error. Please recalibrate your query.")
                                print(f"Error: {str(e)}")
            
            # Chat history display
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            if len(st.session_state.chat_history) > 0:
                st.subheader("💾 Recent Conversations")
                for chat in st.session_state.chat_history[-3:]:
                    with st.expander(f"Q: {chat['question'][:50]}..."):
                        st.write(f"**Response:** {chat['answer']}")
        
        with col_ai2:
            # Performance Analysis
            st.markdown("""
            <div class="ai-container">
                <h3>📈 Performance Analysis</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔥 Compare Algorithms", help="Analyze algorithm performance matrix"):
                st.session_state['run_comparison'] = True
    
    # Algorithm comparison results
    if 'run_comparison' in st.session_state:
        st.markdown("---")
        st.subheader("📊 Algorithm Performance Matrix")
        
        with st.spinner("🧠 Running algorithm comparison..."):
            try:
                comparison_results = pathfinder.compare_algorithms()
                
                # Display results table
                df = pd.DataFrame(comparison_results)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=False
                )
                
                # Performance insights
                st.subheader("⚡ Performance Insights")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fastest_algo = df.loc[df['Average Distance (m)'].idxmin(), 'Algorithm']
                    st.metric("🏆 Shortest Path", str(fastest_algo))
                
                with col2:
                    least_explored = df.loc[df['Average Nodes Explored'].idxmin(), 'Algorithm']
                    st.metric("⚡ Most Efficient", str(least_explored))
                
                with col3:
                    most_explored = df.loc[df['Average Nodes Explored'].idxmax(), 'Algorithm']
                    st.metric("🔍 Most Thorough", str(most_explored))
                
                del st.session_state['run_comparison']
                
            except Exception as e:
                st.error(f"🚨 Comparison error: {str(e)}")
    
    
    # Professional Footer (Dark Theme)
    st.markdown("""
    <div style="
        background-color: #2d2d2d;
        border-top: 1px solid #404040;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        margin-top: 3rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    ">
        <h4 style="color: #ffffff; margin-bottom: 0.5rem; font-weight: 600;">CyberNav: Campus Route AI</h4>
        <p style="color: #cccccc; margin: 0; font-size: 0.9rem;">Powered by Pathfinding Algorithms, OpenStreetMap & Gemini AI</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"🚨 System Error: {str(e)}")
    st.info("Please ensure the OSM data file is properly loaded and all dependencies are installed.")