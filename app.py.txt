import streamlit as st
import pandas as pd
import time

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Workforce MailSync AI", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM HASEEN CSS (PREMIUM STYLING)
# ==========================================
st.markdown(
    """
    <style>
    /* Hiding Default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Background and Font */
    .stApp {
        background-color: #f3f6fc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main Container */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Modern Dashboard Title */
    .dash-title {
        font-size: 38px;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #4f46e5, #9333ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .dash-subtitle {
        color: #64748b;
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 30px;
    }

    /* Beautiful Metric Cards */
    .ai-metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.04);
        border: 1px solid #e2e8f0;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .ai-metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(79, 70, 229, 0.1);
    }
    .metric-value { font-size: 36px; font-weight: 800; color: #1e293b; }
    .metric-label { font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

    /* Custom Gradient Button */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 24px !important;
        width: 100%;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        box-shadow: 0 12px 25px rgba(79, 70, 229, 0.5) !important;
        transform: scale(1.02);
    }

    /* Email Cards Design */
    .email-card {
        background: white;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border-left: 6px solid #4f46e5;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .email-card.leave { border-left-color: #f59e0b; }
    .email-card.mispunch { border-left-color: #ef4444; }
    .email-card.shift { border-left-color: #10b981; }

    .email-details h4 { margin: 0; color: #1e293b; font-size: 18px; font-weight: 700; }
    .email-details p { margin: 4px 0 0 0; color: #64748b; font-size: 14px; }
    
    .ai-badge {
        padding: 6px 12px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
    }
    .badge-leave { background: #fef3c7; color: #d97706; }
    .badge-mispunch { background: #fee2e2; color: #dc2626; }
    .badge-shift { background: #d1fae5; color: #059669; }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# SIDEBAR SETTINGS
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2646/2646141.png", width=60)
    st.markdown("### ⚙️ AI Engine Settings")
    st.text_input("Gemini API Key", type="password", placeholder="Paste your API key here...")
    st.text_input("HR Inbox Email", placeholder="hr@amazon.com")
    st.selectbox("Auto-Reply Mode", ["Fully Automated (Send Direct)", "Draft Only (Require Approval)", "Off"])
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray; font-size:12px;'>System Status: 🟢 <b>Online</b></p>", unsafe_allow_html=True)

# ==========================================
# MAIN DASHBOARD HEADER
# ==========================================
st.markdown('<div class="dash-title">Workforce MailSync AI ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-subtitle">Intelligent Email Parsing & Automated Attendance Actions System</div>', unsafe_allow_html=True)

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="ai-metric-card"><div class="metric-value">142</div><div class="metric-label">Emails Scanned</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="ai-metric-card"><div class="metric-value" style="color:#10b981;">118</div><div class="metric-label">Auto-Resolved</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="ai-metric-card"><div class="metric-value" style="color:#f59e0b;">24</div><div class="metric-label">Pending Review</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="ai-metric-card"><div class="metric-value" style="color:#4f46e5;">98%</div><div class="metric-label">AI Accuracy</div></div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# AI SCANNER SECTION (DEMO)
# ==========================================
if 'scanned' not in st.session_state:
    st.session_state.scanned = False

action_col, text_col = st.columns([3, 7])

with action_col:
    st.markdown("### 🤖 Inbox Sync")
    st.write("Click below to fetch and analyze unread HR emails using AI.")
    if st.button("Fetch & Analyze New Emails ➔"):
        with st.spinner("Connecting to Mail Server..."):
            time.sleep(1)
        with st.spinner("Gemini AI is reading and extracting data..."):
            time.sleep(2)
        st.session_state.scanned = True
        st.success("Analysis Complete! 3 new requests processed.")

with text_col:
    st.markdown("### 📥 Recent Processed Emails")
    
    if not st.session_state.scanned:
        st.info("No new emails processed today. Click 'Fetch & Analyze' to run the AI engine.")
    else:
        # Mocking the AI output into beautiful HTML cards
        html_cards = """
        <!-- Card 1: Mispunch -->
        <div class="email-card mispunch">
            <div class="email-details">
                <h4>Missing Punch on Monday</h4>
                <p><b>From:</b> usman.associate@amazon.com &nbsp; | &nbsp; <b>Extracted ID:</b> 206348020</p>
                <p><i>AI Summary: Employee forgot to punch out due to system error.</i></p>
            </div>
            <div style="text-align: right;">
                <span class="ai-badge badge-mispunch">⚠️ Mispunch</span><br>
                <p style="margin-top:8px; font-size:12px; color:#64748b;">Action: <b>Auto-Replied ✅</b></p>
            </div>
        </div>

        <!-- Card 2: Sick Leave -->
        <div class="email-card leave">
            <div class="email-details">
                <h4>Sick Leave Request - 11th Aug</h4>
                <p><b>From:</b> ahmed.ali@amazon.com &nbsp; | &nbsp; <b>Extracted ID:</b> 206136723</p>
                <p><i>AI Summary: Employee is requesting sick leave for one day due to fever.</i></p>
            </div>
            <div style="text-align: right;">
                <span class="ai-badge badge-leave">🤒 Sick Leave</span><br>
                <p style="margin-top:8px; font-size:12px; color:#64748b;">Action: <b>Updated Roster ✅</b></p>
            </div>
        </div>

        <!-- Card 3: Shift Change -->
        <div class="email-card shift">
            <div class="email-details">
                <h4>Request for 7-Hour Shift Switch</h4>
                <p><b>From:</b> sara.khan@amazon.com &nbsp; | &nbsp; <b>Extracted ID:</b> 205854274</p>
                <p><i>AI Summary: Employee requesting to change configuration to 7-hours.</i></p>
            </div>
            <div style="text-align: right;">
                <span class="ai-badge badge-shift">🔄 Shift Change</span><br>
                <p style="margin-top:8px; font-size:12px; color:#64748b;">Action: <b>Pending Manager Approval ⏳</b></p>
            </div>
        </div>
        """
        st.markdown(html_cards, unsafe_allow_html=True)
