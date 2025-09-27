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
    page_title="Campus Navigation Pro",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-weight: 700;
        font-size: 2.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        color: #e2e8f0;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Section headers */
    .section-header {
        background-color: #f1f5f9;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    .section-header h3 {
        color: #1e293b;
        margin: 0;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        transform: translateY(-1px);
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Map container */
    .map-container {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    
    /* Info panels */
    .info-panel {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    /* Chat styling */
    .stChatMessage {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }
    
    /* Select boxes and inputs */
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #d1d5db;
    }
    
    /* Data tables */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #dcfce7;
        border: 1px solid #86efac;
        border-radius: 8px;
    }
    
    .stError {
        background-color: #fef2f2;
        border: 1px solid #fca5a5;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize pathfinder and Gemini assistant
@st.cache_resource
def initialize_pathfinder():
    return CampusPathfinder("attached_assets/map_1758707724808.osm")

@st.cache_resource
def initialize_gemini():
    try:
        # Check for API key in environment variables (set by Replit Secrets)
        if not os.environ.get("GEMINI_API_KEY"):
            st.warning(" AI Assistant unavailable: GEMINI_API_KEY not configured")
            return None
        return GeminiAssistant()
    except Exception as e:
        st.error(f"Failed to initialize AI Assistant: {str(e)}")
        return None

try:
    pathfinder = initialize_pathfinder()
    gemini = initialize_gemini()
    
    # Professional header
    st.markdown("""
    <div class="main-header">
        <h1> Campus Navigation Pro</h1>
        <p>Advanced pathfinding system with AI-powered assistance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional sidebar for controls
    with st.sidebar:
        st.markdown("""
        <div class="section-header">
            <h3>🎯 Route Planning</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Location selection with professional styling
        st.markdown("**Select Journey Points**")
        locations = list(pathfinder.POIS.keys())
        start_location = st.selectbox(" Start Location", locations, index=0, help="Choose your starting point")
        end_location = st.selectbox(" Destination", locations, index=1, help="Choose your destination")
        
        st.markdown("""
        <div class="section-header">
            <h3> Algorithm Selection</h3>
        </div>
        """, unsafe_allow_html=True)
        
        algorithm = st.selectbox(
            "Pathfinding Algorithm",
            ["A*", "A* (Euclidean)", "A* (Manhattan)", "A* (Combined)", "BFS", "DFS", "UCS"],
            index=0,  # Default to A*
            help="Choose the pathfinding algorithm. A* variants are recommended for optimal routes."
        )
        
        # Professional pathfinding button
        st.markdown("<br>", unsafe_allow_html=True)
        run_pathfinding = st.button(" Find Optimal Path", type="primary", use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Professional comparison section
        st.markdown("""
        <div class="section-header">
            <h3> Performance Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Compare Algorithms", help="Compare performance of different algorithms"):
                st.session_state['run_comparison'] = True
        
        with col_b:
            if st.button(" Compare Heuristics", help="Compare A* heuristic variations"):
                st.session_state['run_heuristic_comparison'] = True
        
        st.markdown("""
        <div class="section-header">
            <h3> AI Campus Assistant</h3>
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
            st.info("🔧 AI Assistant is currently unavailable. Please check that the GEMINI_API_KEY is properly configured.")
            st.chat_input("AI Assistant unavailable...", disabled=True)
        else:
            user_query = st.chat_input("Ask me anything about the campus...")
            
            if user_query:
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": user_query})
                with st.chat_message("user"):
                    st.markdown(user_query)
                
                # Generate AI response
                with st.chat_message("assistant"):
                    with st.spinner(" Processing..."):
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
                            st.error("I apologize, but I encountered an error. Please try rephrasing your question.")
                            print(f"Error: {str(e)}")
        
        # Add chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if len(st.session_state.chat_history) > 0:
            st.subheader(" Recent Conversations")
            for chat in st.session_state.chat_history[-3:]:  # Show last 3 conversations
                with st.expander(f"Q: {chat['question'][:50]}..."):
                    st.write(f"**Answer:** {chat['answer']}")

    # Professional main content area
    col1, col2 = st.columns([2.2, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div class="map-container">
            <h3 style="color: #1e293b; margin-bottom: 1rem; font-weight: 600;"> Interactive Campus Map</h3>
        """, unsafe_allow_html=True)
        
        # Initialize map display
        if 'current_map' not in st.session_state:
            st.session_state['current_map'] = pathfinder.create_base_map()
        
        # Handle pathfinding request
        if run_pathfinding:
            try:
                with st.spinner(f"Finding path using {algorithm}..."):
                    result = pathfinder.find_path(start_location, end_location, algorithm)
                    st.session_state['current_map'] = result['map']
                    st.session_state['path_metrics'] = result['metrics']
                    st.session_state['algorithm_used'] = algorithm
                    
                st.success(f" Optimal path calculated using {algorithm} algorithm!")
            except Exception as e:
                st.error(f" Unable to calculate path: {str(e)}")
        
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
            <h3 style="color: #1e293b; margin-bottom: 1rem; font-weight: 600;"> Route Information</h3>
        """, unsafe_allow_html=True)
        
        # Professional metrics display
        if 'path_metrics' in st.session_state:
            metrics = st.session_state['path_metrics']
            algorithm_used = st.session_state.get('algorithm_used', 'Unknown')
            
            # Metrics in organized columns
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric(" Algorithm", algorithm_used)
                st.metric(" Distance", f"{metrics['distance']:.0f}m")
            with col_m2:
                st.metric(" Time", f"{metrics['time']:.1f} min")
                st.metric(" Explored", f"{metrics['nodes_explored']:,}")
            
            # Professional location details
            st.markdown("---")
            st.markdown("** Journey Details**")
            
            start_info = pathfinder.get_location_info(metrics['start_location'])
            end_info = pathfinder.get_location_info(metrics['end_location'])
            
            st.markdown(f"""
**From:** {start_info['name']}  
**To:** {end_info['name']}  
**Route Status:**  Optimal path found
            """)
        else:
            st.markdown("""
            <div style="padding: 2rem; text-align: center; color: #64748b;">
                <h4> Select Route</h4>
                <p>Choose start and destination points, then click 'Find Optimal Path' to see detailed route information.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display AI response if available
        if 'ai_query' in st.session_state:
            with st.spinner(" AI is thinking..."):
                try:
                    ai_response = gemini.process_query(
                        st.session_state['ai_query'],
                        pathfinder.POIS,
                        pathfinder
                    )
                    st.subheader(" AI Assistant Response")
                    st.write(ai_response)
                    del st.session_state['ai_query']  # Clear after processing
                except Exception as e:
                    st.error(f" AI Error: {str(e)}")
    
    # Algorithm comparison results
    if 'run_comparison' in st.session_state:
        st.markdown("---")
        st.subheader(" Algorithm Performance Comparison")
        
        with st.spinner(" Running algorithm comparison..."):
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
                st.subheader(" Performance Insights")
                
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
                
                del st.session_state['run_comparison']  # Clear after processing
                
            except Exception as e:
                st.error(f" Comparison Error: {str(e)}")
    
    # Heuristic comparison results
    if 'run_heuristic_comparison' in st.session_state:
        st.markdown("---")
        st.subheader(" A* Heuristic Comparison")
        
        with st.spinner(" Running heuristic comparison..."):
            try:
                heuristic_results = pathfinder.compare_heuristics()
                
                # Display results table
                df_heuristic = pd.DataFrame(heuristic_results)
                st.dataframe(
                    df_heuristic,
                    use_container_width=True,
                    hide_index=False
                )
                
                # Heuristic insights
                st.subheader(" Heuristic Analysis")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    best_heuristic = df_heuristic.loc[df_heuristic['Average Distance (m)'].idxmin(), 'Heuristic Type']
                    st.metric(" Best Distance", str(best_heuristic))
                
                with col2:
                    most_efficient = df_heuristic.loc[df_heuristic['Average Nodes Explored'].idxmin(), 'Heuristic Type']
                    st.metric(" Most Efficient", str(most_efficient))
                
                with col3:
                    best_efficiency = df_heuristic.loc[df_heuristic['Efficiency Score'].idxmax(), 'Heuristic Type']
                    st.metric(" Best Efficiency Score", str(best_efficiency))
                
                # Detailed analysis
                st.subheader(" Detailed Heuristic Analysis")
                
                st.write("**Key Insights:**")
                st.write("• **Euclidean Distance**: Calculates straight-line distance between points")
                st.write("• **Manhattan Distance**: Sum of horizontal and vertical distances")
                st.write("• **Combined Heuristic**: Weighted combination (70% Euclidean + 30% Manhattan)")
                st.write("• **Efficiency Score**: Distance per node explored (higher = better path quality per exploration)")
                
                del st.session_state['run_heuristic_comparison']  # Clear after processing
                
            except Exception as e:
                st.error(f" Heuristic Comparison Error: {str(e)}")
    
    # Professional footer
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-top: 3rem;
        border: 1px solid #e2e8f0;
    ">
        <h4 style="color: #1e293b; margin-bottom: 0.5rem;">Campus Navigation Pro</h4>
        <p style="color: #64748b; margin: 0;">Powered by Advanced Pathfinding Algorithms, OpenStreetMap & Gemini AI</p>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem;">Professional routing system for educational institutions</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f" Application Error: {str(e)}")
    st.info("Please ensure the OSM file is properly loaded and all dependencies are installed.")
