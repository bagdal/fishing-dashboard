#!/usr/bin/env python3
"""
IBCC 2026 Fishing Contest Dashboard - Professional Version
Modern Streamlit dashboard with real-time data, charts, and dark/light mode
"""

import streamlit as st
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="IBCC 2026 - Professional Dashboard",
    page_icon="🎣",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Theme configuration
THEME_CONFIG = {
    'dark': {
        'bg_primary': '#0a192f',
        'bg_secondary': '#112240',
        'bg_card': '#1d3557',
        'text_primary': '#ccd6f6',
        'text_secondary': '#8892b0',
        'accent': '#64ffda',
        'accent_secondary': '#00b4d8',
        'warning': '#f59e0b',
        'success': '#10b981',
        'border': '#233554'
    },
    'light': {
        'bg_primary': '#f8fafc',
        'bg_secondary': '#e2e8f0',
        'bg_card': '#ffffff',
        'text_primary': '#1e293b',
        'text_secondary': '#64748b',
        'accent': '#0ea5e9',
        'accent_secondary': '#0284c7',
        'warning': '#f59e0b',
        'success': '#10b981',
        'border': '#cbd5e1'
    }
}

theme = THEME_CONFIG[st.session_state.theme]

# Custom CSS with theme support
def get_css(theme):
    bg_primary = theme['bg_primary']
    bg_secondary = theme['bg_secondary']
    bg_card = theme['bg_card']
    text_primary = theme['text_primary']
    text_secondary = theme['text_secondary']
    accent = theme['accent']
    accent_secondary = theme['accent_secondary']
    warning = theme['warning']
    success = theme['success']
    border = theme['border']
    
    return f"""
<style>
    .main {{
        background-color: {bg_primary};
        color: {text_primary};
    }}
    .stApp {{
        background-color: {bg_primary};
    }}
    .stMetric {{
        background-color: {bg_secondary};
        padding: 20px;
        border-radius: 15px;
        border: 2px solid {border};
        margin: 10px 0;
        color: {text_primary};
    }}
    .metric-card {{
        background: linear-gradient(135deg, {accent} 0%, {accent_secondary} 100%);
        padding: 25px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-5px);
    }}
    .big-fish {{
        background: linear-gradient(135deg, {warning} 0%, #d97706 100%);
        padding: 25px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    .header {{
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, {bg_card} 0%, {bg_secondary} 100%);
        border-radius: 15px;
        margin-bottom: 20px;
        border: 2px solid {border};
    }}
    .info-box {{
        background-color: {bg_secondary};
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid {accent};
        margin: 15px 0;
        color: {text_primary};
    }}
    .warning-box {{
        background-color: {bg_secondary};
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid {warning};
        margin: 15px 0;
        color: {text_primary};
    }}
    .success-box {{
        background-color: {bg_secondary};
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid {success};
        margin: 15px 0;
        color: {text_primary};
    }}
    .stButton>button {{
        background: linear-gradient(135deg, {accent} 0%, {accent_secondary} 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }}
    .stSelectbox>div>div>select {{
        background-color: {bg_secondary};
        color: {text_primary};
        border: 1px solid {border};
    }}
    .stCheckbox>label {{
        color: {text_primary};
    }}
    h1, h2, h3 {{
        color: {text_primary};
    }}
    p, span, div {{
        color: {text_primary};
    }}
    .stCaption {{
        color: {text_secondary};
    }}
    @media (max-width: 768px) {{
        .stMetric {{
            padding: 15px;
            font-size: 14px;
        }}
        .metric-card {{
            padding: 20px;
        }}
    }}
</style>
"""

st.markdown(get_css(theme), unsafe_allow_html=True)



# Data fetching functions
def get_weather_data():
    """Fetch weather data from met.hu"""
    try:
        url = "https://www.met.hu/idojaras/tavaink/balaton/viharjelzes/index.php"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Try to extract storm warning level
            warning_text = soup.get_text()
            if 'Nincs érvényben riasztás' in warning_text:
                return {'status': 'safe', 'level': 0, 'message': 'Nincs viharjelzés'}
            elif 'elsőfokú' in warning_text.lower():
                return {'status': 'warning', 'level': 1, 'message': 'Elsőfokú viharjelzés'}
            elif 'másodfokú' in warning_text.lower():
                return {'status': 'danger', 'level': 2, 'message': 'Másodfokú viharjelzés'}
            else:
                return {'status': 'unknown', 'level': 0, 'message': 'Adat nem elérhető'}
        return {'status': 'error', 'level': 0, 'message': 'Hiba a lekérésnél'}
    except Exception as e:
        return {'status': 'error', 'level': 0, 'message': f'Hiba: {str(e)}'}

def get_contest_data():
    """Fetch contest data from fishinda"""
    try:
        url = "https://contest.fishinda.com/ibcc-2026"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            
            # Extract data using regex patterns
            import re
            
            # Try to find total weight (pattern: "10560.36 kg")
            total_weight_match = re.search(r'(\d+\.?\d*)\s*kg', text)
            if total_weight_match:
                total_weight = float(total_weight_match.group(1))
            else:
                total_weight = 0
            
            # Try to find catches (pattern: "791 pcs" or similar)
            catches_match = re.search(r'(\d+)\s*(?:pcs|pieces|db)', text, re.IGNORECASE)
            if catches_match:
                catches = int(catches_match.group(1))
            else:
                catches = 0
            
            # Try to find average
            average_match = re.search(r'Average[^\d]*(\d+\.?\d*)', text, re.IGNORECASE)
            if average_match:
                average = float(average_match.group(1))
            else:
                average = 0
            
            # Try to find biggest fish (look for "Biggest" keyword nearby)
            biggest_match = re.search(r'Biggest[^\d]*(\d+\.?\d*)\s*kg', text, re.IGNORECASE)
            if biggest_match:
                largest_fish = float(biggest_match.group(1))
            else:
                # Fallback: look for kg values under 100 (likely individual fish)
                kg_matches = re.findall(r'(\d+\.?\d*)\s*kg', text)
                if kg_matches:
                    # Filter out very large values (total weight) and take the largest reasonable fish weight
                    fish_weights = [float(x) for x in kg_matches if float(x) < 100]
                    if fish_weights:
                        largest_fish = max(fish_weights)
                    else:
                        largest_fish = 0
                else:
                    largest_fish = 0
            
            # Use catches as participants proxy
            participants = catches
            
            return {
                'status': 'success',
                'participants': participants,
                'caught': catches,
                'largest': largest_fish,
                'total_weight': total_weight,
                'average': average
            }
        return {'status': 'error', 'participants': 0, 'caught': 0, 'largest': 0, 'total_weight': 0, 'average': 0}
    except Exception as e:
        return {'status': 'error', 'participants': 0, 'caught': 0, 'largest': 0, 'total_weight': 0, 'average': 0}

def create_weather_chart(weather_data):
    """Create weather status chart"""
    if weather_data['status'] == 'error':
        return None
    
    fig = go.Figure(go.Indicator(
        mode = "number+gauge",
        value = weather_data['level'],
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Viharjelzés szint"},
        gauge = {
            'axis': {'range': [None, 2]},
            'bar': {'color': theme['accent']},
            'steps': [
                {'range': [0, 1], 'color': theme['bg_secondary']},
                {'range': [1, 2], 'color': theme['warning']},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 2
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor=theme['bg_primary'],
        font={'color': theme['text_primary']}
    )
    return fig

def create_contest_chart(contest_data):
    """Create contest statistics chart"""
    if contest_data['status'] == 'error':
        return None
    
    categories = ['Fogott halak', 'Teljes súly (kg)', 'Átlag (kg)', 'Legnagyobb hal (kg)']
    values = [contest_data['caught'], contest_data['total_weight'], contest_data['average'], contest_data['largest']]
    
    fig = go.Figure(data=[
        go.Bar(name='Statisztikák', x=categories, y=values,
               marker_color=[theme['accent'], theme['accent_secondary'], theme['success'], theme['warning']])
    ])
    
    fig.update_layout(
        title="Verseny Statisztikák",
        xaxis_title="Kategória",
        yaxis_title="Érték",
        paper_bgcolor=theme['bg_primary'],
        plot_bgcolor=theme['bg_secondary'],
        font={'color': theme['text_primary']}
    )
    return fig

def main():
    # Sidebar
    with st.sidebar:
        st.title("🎣 IBCC 2026")
        st.markdown("---")
        
        # Theme toggle
        if st.button(f"🌙 {'Dark Mode' if st.session_state.theme == 'light' else 'Light Mode'}"):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.rerun()
        
        st.markdown("---")
        
        # Auto-refresh
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=True)
        
        st.markdown("---")
        
        # Navigation
        st.subheader("Navigáció")
        page = st.radio(
            "Válassz oldalt:",
            ["📊 Dashboard", "⛈️ Viharjelzés", "🎣 Verseny Adatok", "ℹ️ Információk"],
            label_visibility="collapsed"
        )
    
    # Header
    st.markdown(f"""
    <div class="header">
        <h1>🎣 IBCC 2026 Horgászverseny</h1>
        <p>International Carp Championship - Professional Dashboard</p>
        <p style="color: {theme['text_secondary']}; font-size: 14px;">🕒 Frissítve: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if page == "📊 Dashboard":
        # Main dashboard with overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            weather = get_weather_data()
            if weather['status'] == 'safe':
                st.markdown(f"""
                <div class="success-box">
                    <h3>⛈️ Viharjelzés</h3>
                    <p>{weather['message']}</p>
                </div>
                """, unsafe_allow_html=True)
            elif weather['status'] == 'warning':
                st.markdown(f"""
                <div class="warning-box">
                    <h3>⛈️ Viharjelzés</h3>
                    <p>{weather['message']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="info-box">
                    <h3>⛈️ Viharjelzés</h3>
                    <p>{weather['message']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            contest = get_contest_data()
            if contest['status'] == 'success':
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🎣 Fogott halak darab száma</h3>
                    <p style="font-size: 32px; font-weight: bold;">{contest['caught']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if contest['status'] == 'success':
                st.markdown(f"""
                <div class="big-fish">
                    <h3>🐟 Legnagyobb hal</h3>
                    <p style="font-size: 32px; font-weight: bold;">{contest['largest']} kg</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            weather_chart = create_weather_chart(weather)
            if weather_chart:
                st.plotly_chart(weather_chart, width='stretch')
        
        with col2:
            contest_chart = create_contest_chart(contest)
            if contest_chart:
                st.plotly_chart(contest_chart, width='stretch')
    
    elif page == "⛈️ Viharjelzés":
        st.subheader("⛈️ Részletes Viharjelzés")
        st.markdown(f"""
        <div class="info-box">
            <h3>Met.hu Balaton Viharjelzés</h3>
            <p>A BM Országos Katasztrófavédelmi Főigazgatóság minden év április 1-től október 31-ig üzemelteti a viharjelző rendszereket a Balatonon.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <iframe 
            src="https://www.met.hu/idojaras/tavaink/balaton/viharjelzes/index.php" 
            width="100%" 
            height="600" 
            style="border:2px solid {theme['border']}; border-radius:15px;"
            scrolling="yes"
        ></iframe>
        """, unsafe_allow_html=True)
    
    elif page == "🎣 Verseny Adatok":
        st.subheader("🎣 IBCC 2026 Horgászverseny - Élő Statisztikák")
        
        st.markdown("""
        <iframe 
            src="https://contest.fishinda.com/ibcc-2026" 
            width="100%" 
            height="800" 
            style="border:2px solid {theme['border']}; border-radius:15px;"
            scrolling="yes"
        ></iframe>
        """, unsafe_allow_html=True)
    
    elif page == "ℹ️ Információk":
        st.subheader("ℹ️ Információk")
        
        st.markdown(f"""
        <div class="info-box">
            <h3>🎣 Verseny Információk</h3>
            <p><strong>Verseny:</strong> IBCC 2026 International Carp Championship</p>
            <p><strong>Helyszín:</strong> Fishinda</p>
            <p><strong>Adatok:</strong> Valós idejű frissítés</p>
            <p><strong>Platform:</strong> Mobilbarát modern dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="warning-box">
            <h3>⛈️ Viharjelzés</h3>
            <p><strong>Forrás:</strong> Magyar Meteorológiai Szolgálat (met.hu)</p>
            <p><strong>Térkép:</strong> Balaton viharjelző rendszer</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="success-box">
            <h3>📱 Technikai Információk</h3>
            <p><strong>Verzió:</strong> Professional v2.0</p>
            <p><strong>Téma:</strong> {'Dark Mode' if st.session_state.theme == 'dark' else 'Light Mode'}</p>
            <p><strong>Auto-refresh:</strong> {'Bekapcsolva' if auto_refresh else 'Kikapcsolva'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(30)
        st.rerun()


if __name__ == "__main__":
    main()
