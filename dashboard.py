"""
╔══════════════════════════════════════════════════════════════════════╗
║        SECURE REAL-TIME SPAR APPLIANCESURING MD STRATEGIC DASHBOARD         ║
║        Built with Streamlit + Plotly + Google Sheets API             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone, timedelta, timedelta
import time
import hashlib
import json
import io
import base64

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MD Strategic Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── THEME & GLOBAL CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Import Fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');
  @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

  /* ── Root Variables ── */
  :root {
    --bg-primary:    #0a0e1a;
    --bg-card:       #111827;
    --bg-card2:      #1a2235;
    --accent-cyan:   #00d4ff;
    --accent-amber:  #ffb800;
    --accent-green:  #00e676;
    --accent-red:    #ff3d5a;
    --accent-purple: #a78bfa;
    --text-primary:  #f0f4ff;
    --text-muted:    #8899bb;
    --border:        rgba(0,212,255,0.15);
    --glow-cyan:     0 0 20px rgba(0,212,255,0.3);
    --glow-amber:    0 0 20px rgba(255,184,0,0.3);
  }

  /* ── Global Reset ── */
  .stApp { background: var(--bg-primary) !important; }
  button
  .main .block-container { padding: 1rem 1.5rem 2rem !important; max-width: 100% !important; }
  * { font-family: 'DM Sans', sans-serif !important; color: var(--text-primary); }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1526 0%, #111827 100%) !important;
    border-right: 1px solid var(--border);
  }
  section[data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem; }

  /* ── Hide Default Header ── */
  #MainMenu, footer, header { visibility: hidden; }

  /* Hide keyboard_double_arrow tooltip */
  .st-emotion-cache-fix, 
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  div[class*="StatusWidget"],
  div[class*="toolbar"],
  .viewerBadge_container__1QSob,
  #MainMenu { display: none !important; visibility: hidden !important; }

  /* Hide keyboard_double_arrow tooltip */
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  div[class*="StatusWidget"],
  div[class*="toolbar"] { display: none !important; visibility: hidden !important; }

  /* Hide ALL sidebar toggle buttons - clean single rule */
  [data-testid="collapsedControl"],
  [data-testid="collapsedControl"] *,
  [data-testid="baseButton-headerNoPadding"],
  button[kind="header"] {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
  }

  /* Always keep sidebar open - hide collapse/expand buttons */
  [data-testid="collapsedControl"] { display: none !important; }
  [data-testid="baseButton-headerNoPadding"] { display: none !important; }
  button[title="Close sidebar"] { display: none !important; }
  
  /* Sidebar always visible */
  section[data-testid="stSidebar"] {
    display: flex !important;
    visibility: visible !important;
    transform: none !important;
    min-width: 280px !important;
    max-width: 320px !important;
  }
  [data-testid="collapsedControl"] svg {
    fill: #000 !important;
    width: 16px !important;
    height: 16px !important;
  }
  [data-testid="collapsedControl"]:hover {
    background: #00ffee !important;
    width: 34px !important;
  }

  /* ── Sidebar Arrow Button Fix ── */
  div[data-testid="collapsedControl"],
  button[data-testid="collapsedControl"],
  [data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 9999 !important;
    background: #00d4ff !important;
    border-radius: 0 8px 8px 0 !important;
    position: fixed !important;
    left: 0 !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    width: 24px !important;
    height: 60px !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    border: none !important;
  }
  [data-testid="collapsedControl"] svg {
    fill: #000 !important;
    color: #000 !important;
  }
  
  

  
  button

  /* ── Top Nav Bar ── */
  .topbar {
    background: linear-gradient(90deg, #0d1526 0%, #111827 50%, #0d1526 100%);
    border-bottom: 1px solid var(--border);
    padding: 0.75rem 1.5rem;
    display: flex; align-items: center; justify-content: space-between;
    margin: -1rem -1.5rem 1.5rem -1.5rem;
    box-shadow: 0 2px 20px rgba(0,0,0,0.5);
  }
  .topbar-logo {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.6rem; letter-spacing: 3px;
    color: var(--accent-cyan) !important;
    text-shadow: var(--glow-cyan);
  }
  .topbar-sub { font-size: 0.72rem; color: var(--text-muted) !important; letter-spacing: 2px; text-transform: uppercase; }
  .topbar-time {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem; color: var(--accent-cyan) !important;
    background: rgba(0,212,255,0.08); border: 1px solid var(--border);
    padding: 0.3rem 0.8rem; border-radius: 6px;
  }

  /* ── KPI Metric Cards ── */
  .kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .kpi-card:hover { transform: translateY(-2px); box-shadow: var(--glow-cyan); }
  .kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
  }
  .kpi-label {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 2px;
    text-transform: uppercase; color: var(--text-muted) !important; margin-bottom: 0.5rem;
  }
  .kpi-value {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 2.2rem; line-height: 1; color: var(--accent-cyan) !important;
    text-shadow: var(--glow-cyan);
  }
  .kpi-delta {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem; margin-top: 0.4rem;
  }
  .kpi-delta.positive { color: var(--accent-green) !important; }
  .kpi-delta.negative { color: var(--accent-red) !important; }
  .kpi-icon {
    position: absolute; right: 1rem; top: 50%; transform: translateY(-50%);
    font-size: 2.5rem; opacity: 0.12;
  }

  /* ── Alert Banners ── */
  .alert-critical {
    background: linear-gradient(135deg, rgba(255,61,90,0.15) 0%, rgba(255,61,90,0.05) 100%);
    border: 1px solid rgba(255,61,90,0.5);
    border-left: 4px solid var(--accent-red);
    border-radius: 8px; padding: 0.8rem 1.2rem; margin-bottom: 0.8rem;
    display: flex; align-items: center; gap: 0.8rem;
  }
  .alert-warning {
    background: linear-gradient(135deg, rgba(255,184,0,0.15) 0%, rgba(255,184,0,0.05) 100%);
    border: 1px solid rgba(255,184,0,0.5);
    border-left: 4px solid var(--accent-amber);
    border-radius: 8px; padding: 0.8rem 1.2rem; margin-bottom: 0.8rem;
    display: flex; align-items: center; gap: 0.8rem;
  }
  .alert-ok {
    background: linear-gradient(135deg, rgba(0,230,118,0.12) 0%, rgba(0,230,118,0.04) 100%);
    border: 1px solid rgba(0,230,118,0.4);
    border-left: 4px solid var(--accent-green);
    border-radius: 8px; padding: 0.8rem 1.2rem; margin-bottom: 0.8rem;
  }
  .alert-icon { font-size: 1.2rem; }
  .alert-text { font-size: 0.85rem; font-weight: 500; }

  /* ── Section Headers ── */
  .section-title {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem; letter-spacing: 3px;
    color: var(--text-muted) !important;
    text-transform: uppercase; margin-bottom: 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
  }

  /* ── Chart Containers ── */
  .chart-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem;
    margin-bottom: 1rem;
  }

  /* ── Login Screen ── */
  .login-container {
    max-width: 420px; margin: 4rem auto;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px; padding: 2.5rem;
    box-shadow: 0 8px 60px rgba(0,0,0,0.6), var(--glow-cyan);
    position: relative; overflow: hidden;
  }
  .login-container::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple), var(--accent-amber));
  }
  .login-logo {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 2.4rem; letter-spacing: 4px;
    color: var(--accent-cyan) !important;
    text-shadow: var(--glow-cyan);
    text-align: center; margin-bottom: 0.2rem;
  }
  .login-subtitle {
    text-align: center; font-size: 0.72rem;
    color: var(--text-muted) !important;
    letter-spacing: 3px; text-transform: uppercase; margin-bottom: 2rem;
  }

  /* ── Multiselect Tags Fix ── */
  span[data-baseweb="tag"] {
    background: rgba(0,212,255,0.12) !important;
    border: 1px solid rgba(0,212,255,0.35) !important;
    border-radius: 6px !important;
    color: #00d4ff !important;
    font-size: 0.75rem !important;
  }
  span[data-baseweb="tag"] span { color: #00d4ff !important; }
  span[data-baseweb="tag"] button { color: #00d4ff !important; }
  
  /* Download/Export buttons fix */
  section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #1a2235 0%, #0d1526 100%) !important;
    color: #00d4ff !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    font-size: 0.8rem !important;
    padding: 0.5rem !important;
    width: 100% !important;
  }
  section[data-testid="stSidebar"] .stButton > button:hover {
    border-color: #00d4ff !important;
    box-shadow: 0 0 10px rgba(0,212,255,0.2) !important;
  }

  /* ── Streamlit Input Overrides ── */
  .stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-size: 0.9rem !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 0 1px var(--accent-cyan) !important;
  }
  .stButton > button {
    background: #1a2235 !important;
    color: #00d4ff !important;
    border: 1px solid #00d4ff !important;
    border-radius: 8px !important;
    font-size: 1.2rem !important;
    padding: 0.3rem 0.6rem !important;
    width: auto !important;
    min-width: 42px !important;
    height: 42px !important;
  }

  .stButton > button {
    background: linear-gradient(135deg, #1a3a4a 0%, #0d2535 100%) !important;
    color: var(--accent-cyan) !important; border: 1px solid var(--accent-cyan) !important; font-weight: 700 !important;
    border: none !important; border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important; width: 100%;
    letter-spacing: 1px; text-transform: uppercase; font-size: 0.85rem !important;
    transition: all 0.2s !important;
  }
  .stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: var(--glow-cyan) !important;
  }
  .stSelectbox > div > div, .stMultiSelect > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
  }
  .stDateInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important; color: var(--text-primary) !important;
  }
  .stSlider > div { color: var(--accent-cyan); }

  /* ── Sidebar Labels ── */
  .sidebar-section {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: var(--text-muted) !important;
    margin: 1.2rem 0 0.4rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem;
  }

  /* ── Status Badge ── */
  .status-live {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,230,118,0.1); border: 1px solid rgba(0,230,118,0.3);
    border-radius: 20px; padding: 3px 10px;
    font-size: 0.7rem; font-weight: 600; color: var(--accent-green) !important;
    letter-spacing: 1px; text-transform: uppercase;
  }
  .pulse-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--accent-green);
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
  }

  /* ── Table Styling ── */
  .stDataFrame { border: 1px solid var(--border) !important; border-radius: 8px; }
  .dataframe thead tr th {
    background: var(--bg-card2) !important;
    font-size: 0.75rem !important; font-weight: 600 !important;
    letter-spacing: 1px !important; text-transform: uppercase;
  }

  /* ── Mobile Responsive ── */
  @media (max-width: 768px) {
    .main .block-container { padding: 0.5rem !important; }
    .kpi-value { font-size: 1.6rem !important; }
    .topbar-logo { font-size: 1.2rem !important; }
    .topbar-time { display: none; }
  }
</style>
""", unsafe_allow_html=True)

# ─── CREDENTIALS CONFIG ─────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_users_from_sheet():
    """Users sheet se login credentials load karo — har 1 minute mein refresh."""
    try:
        client = get_gspread_client()
        if client is None:
            raise Exception("No client")
        sheet = client.open_by_key(USERS_SHEET_ID).worksheet("Users")
        data = sheet.get_all_values()
        if not data or len(data) < 2:
            raise Exception("Empty")
        users = {}
        roles = {}
        for row in data[1:]:
            if len(row) >= 3 and row[0].strip():
                username = row[0].strip()
                password = row[1].strip()
                role     = row[2].strip()
                users[username] = hashlib.sha256(password.encode()).hexdigest()
                roles[username] = role
        return users, roles
    except Exception:
        return {
            "md_admin": hashlib.sha256("Admin@2024!".encode()).hexdigest(),
        }, {"md_admin": "MD / Director"}

USERS, USER_ROLES = load_users_from_sheet()

# ─── GOOGLE SHEET CONFIG ────────────────────────────────────────────────────────
# ✅ Replace these with your actual values
SPREADSHEET_ID   = "1W3Du4mxVPkxSaKdgr-BzeFoN_kamiZaBF3oM47GcB8U"
USERS_SHEET_ID   = "1_ucYa-nV23ZIajEpmLBf7_I91S72ohV1DYwIc_uqdyo"
CURRENT_SHEET    = "Production_Data"
ARCHIVE_SHEETS   = ["Archive_Prod_Feb_2026"]
PLAN_SHEET       = "Plan_Data"
REPAIR_SHEET     = "Repairing_Testing"  # Add as needed

REQUIRED_COLUMNS = [
    "Timestamp", "SO Number", "Company Serial Number",
    "Customer Serial Number", "Testing Time", "Status",
    "Reject Reason", "Cleaning", "Manual", "Tested By"
]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

# ─── AUTH HELPERS ───────────────────────────────────────────────────────────────
def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def authenticate(username: str, password: str) -> bool:
    return USERS.get(username) == hash_password(password)

def login_screen():
    """Renders the professional login UI."""
    st.markdown("""
    <style>
      /* Centre content for login */
      .main .block-container { display:flex; align-items:center; justify-content:center; min-height:90vh; }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.4, 1])
    with col_c:
        st.markdown('<div style="text-align:center;margin-bottom:0.5rem;"><img src="data:image/png;base64,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" style="height:70px;width:70px;object-fit:contain;"/></div><div class="login-logo">SPAR APPLIANCES</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Spar Appliances Command Centre</div>', unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown('<p style="font-size:0.8rem;color:#8899bb;margin-bottom:0.3rem;">USERNAME</p>', unsafe_allow_html=True)
            username = st.text_input("", placeholder="Enter your username", label_visibility="collapsed")
            st.markdown('<p style="font-size:0.8rem;color:#8899bb;margin:0.6rem 0 0.3rem;">PASSWORD</p>', unsafe_allow_html=True)
            password = st.text_input("", placeholder="••••••••••", type="password", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🔐  AUTHENTICATE")

        if submitted:
            if authenticate(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"]      = username
                st.session_state["role"]          = USER_ROLES.get(username, "Viewer")
                st.session_state["login_time"]    = datetime.now(timezone(timedelta(hours=5,minutes=30))).strftime("%d %b %Y, %H:%M")
                st.rerun()
            else:
                st.markdown("""
                <div class="alert-critical">
                  <span class="alert-icon">🚫</span>
                  <span class="alert-text">Invalid credentials. Please try again.</span>
                </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;margin-top:1.5rem;font-size:0.7rem;color:#445577;">
          🔒 Secured Access Only &nbsp;|&nbsp; Contact IT for credentials
        </div>""", unsafe_allow_html=True)

# ─── GOOGLE SHEETS CONNECTION ───────────────────────────────────────────────────
def get_gspread_client():
    """
    Authenticates with Google Sheets API using service account credentials.
    Store your service account JSON in .streamlit/secrets.toml as:

        [gcp_service_account]
        type = "service_account"
        project_id = "your-project-id"
        private_key_id = "..."
        private_key = "-----BEGIN RSA PRIVATE KEY-----\\n..."
        client_email = "your-sa@project.iam.gserviceaccount.com"
        ...
    """
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"❌ Google Sheets auth failed: {e}")
        return None

@st.cache_data(ttl=600)   # ← 10-minute TTL cache
def fetch_sheet_data(sheet_name: str) -> pd.DataFrame:
    """Fetches a single sheet and returns a raw DataFrame (no cleaning)."""
    try:
        client = get_gspread_client()
        if client is None:
            return pd.DataFrame()
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        # Handle duplicate/empty headers
        data = sheet.get_all_values()
        if not data:
            return pd.DataFrame()
        
        headers = data[0]
        # Fix empty/duplicate headers
        seen = {}
        clean_headers = []
        for i, h in enumerate(headers):
            h = str(h).strip()
            if h == '' or h is None:
                h = f'Col_{i}'
            if h in seen:
                seen[h] += 1
                h = f'{h}_{seen[h]}'
            else:
                seen[h] = 0
            clean_headers.append(h)
        
        df = pd.DataFrame(data[1:], columns=clean_headers)
        df = df[df[clean_headers[0]].astype(str).str.strip() != '']  # Remove empty rows
        return df
    except Exception as e:
        st.warning(f"⚠️ Could not load sheet '{sheet_name}': {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def fetch_all_data(include_archives: bool = False) -> pd.DataFrame:
    """Fetches and merges Production_Data + Plan_Data + Repairing_Testing."""
    # Fetch production data
    prod_df   = fetch_sheet_data(CURRENT_SHEET)
    plan_df   = fetch_sheet_data(PLAN_SHEET)
    repair_df = fetch_sheet_data(REPAIR_SHEET)

    if include_archives:
        for sheet in ARCHIVE_SHEETS:
            arch_df = fetch_sheet_data(sheet)
            if not arch_df.empty:
                arch_df["_source_sheet"] = sheet
                # SO Number case normalize
                arch_df["SO Number"] = arch_df["SO Number"].astype(str).str.strip().str.upper()
                prod_df = pd.concat([prod_df, arch_df], ignore_index=True)

    if prod_df.empty:
        return pd.DataFrame()

    combined = _clean_dataframe(prod_df, plan_df, repair_df)
    return combined

def _clean_dataframe(prod_df: pd.DataFrame, plan_df: pd.DataFrame, repair_df: pd.DataFrame) -> pd.DataFrame:
    """Merges all 3 sheets and computes KPI columns."""

    # ── Clean Production Data ──
    prod_df["_source_sheet"] = "Production_Data"
    # SO Number case normalize — SO-1001, so-1001, So-1005 sab upper ho jayenge
    prod_df["SO Number"] = prod_df["SO Number"].astype(str).str.strip().str.upper()
    # Mixed format fix — "01/03/2026" aur "01/03/2026 10:45:29" dono handle karo
    def parse_timestamp(ts):
        if pd.isnull(ts) or str(ts).strip() == "":
            return pd.NaT
        ts = str(ts).strip()
        for fmt in ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y",
                    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                return pd.to_datetime(ts, format=fmt)
            except:
                continue
        return pd.to_datetime(ts, dayfirst=True, errors="coerce")

    prod_df["Timestamp"] = prod_df["Timestamp"].apply(parse_timestamp)
    prod_df["Date"]      = pd.to_datetime(prod_df["Timestamp"].dt.date)

    # Shift — Timestamp mein time nahi hai, default "Day" rakho
    prod_df["Shift"] = "Day"

    # Status — Production_Data mein sirf PASS hai
    # FAIL wale Repairing_Testing mein hain — wahan se count karenge
    prod_df["Status_Clean"] = prod_df["Status"].astype(str).str.strip().str.upper()
    prod_df["Is_Pass"] = prod_df["Status_Clean"].isin(["PASS", "OK", "PASSED", "GOOD", "P"])
    prod_df["Is_Fail"] = False  # FAIL Repairing_Testing se aayega

    # ── Merge Plan Data (SO Number → Model Name, Plan Qty, Unit Price) ──
    if not plan_df.empty:
        plan_df["SO Number"] = plan_df["SO Number"].astype(str).str.strip()
        prod_df["SO Number"] = prod_df["SO Number"].astype(str).str.strip()

        # Get Unit Price from Settings if available, else default
        if "Unit Price" in plan_df.columns:
            plan_df["Unit_Price"] = pd.to_numeric(plan_df["Unit Price"], errors="coerce").fillna(5000)
        elif "Unit_Price" in plan_df.columns:
            plan_df["Unit_Price"] = pd.to_numeric(plan_df["Unit_Price"], errors="coerce").fillna(5000)
        else:
            plan_df["Unit_Price"] = 5000

        prod_df = prod_df.merge(
            plan_df[["SO Number", "Model Name", "Plan Qty", "Unit_Price"]].drop_duplicates("SO Number"),
            on="SO Number", how="left"
        )
        prod_df["Model_Name"] = prod_df["Model Name"].fillna("Unknown")
        prod_df["Target_Qty"] = pd.to_numeric(prod_df["Plan Qty"], errors="coerce").fillna(0)
        prod_df["Unit_Price"] = prod_df["Unit_Price"].fillna(5000)
    else:
        prod_df["Model_Name"] = prod_df.get("SO Number", "Unknown")
        prod_df["Target_Qty"] = 0
        prod_df["Unit_Price"] = 5000

    # ── Repair/Rejection from Repairing_Testing ──
    if not repair_df.empty:
        repair_df["Timestamp"] = pd.to_datetime(
            repair_df["Timestamp"], errors="coerce", dayfirst=True)
        repair_df["Date"] = pd.to_datetime(repair_df["Timestamp"].dt.date)

        # SO number column — different case handle karo
        so_col = "SO number" if "SO number" in repair_df.columns else "SO Number"
        repair_df["SO Number"] = repair_df[so_col].astype(str).str.strip()

        # Har unit jo repair mein gayi = 1 rejection
        repair_counts = repair_df.groupby(
            ["Date", "SO Number"]).size().reset_index(name="Rejection_Qty_Repair")

        prod_df = prod_df.merge(repair_counts, on=["Date", "SO Number"], how="left")
        prod_df["Rejection_Qty_Repair"] = prod_df["Rejection_Qty_Repair"].fillna(0)
        prod_df["Is_Fail_Repair"]       = prod_df["Rejection_Qty_Repair"] > 0
        prod_df["Downtime_Minutes"]     = prod_df["Rejection_Qty_Repair"] * 15
        prod_df["Downtime_Reason"]      = prod_df["Rejection_Qty_Repair"].apply(
            lambda x: "None" if x == 0 else "Repair/Rework")
    else:
        prod_df["Rejection_Qty_Repair"] = 0
        prod_df["Is_Fail_Repair"]       = False
        prod_df["Downtime_Minutes"]     = 0
        prod_df["Downtime_Reason"]      = "None"

    # ── Step 1: SO level summary (Rejection from Repair sheet) ──
    so_summary = prod_df.groupby(
        ["SO Number", "Model_Name", "Unit_Price", "Target_Qty"]
    ).agg(
        Production_Qty   = ("Is_Pass", "count"),
        Good_Units       = ("Is_Pass", "sum"),
        Rejection_Qty    = ("Rejection_Qty_Repair", "sum"),
        Downtime_Minutes = ("Downtime_Minutes", "sum"),
    ).reset_index()

    so_summary["Downtime_Reason"] = so_summary["Downtime_Minutes"].apply(
        lambda x: "None" if x == 0 else "Repair/Rework")
    so_summary["Shift"] = "Day"

    # Use latest date per SO for Date column
    so_dates = prod_df.groupby("SO Number")["Date"].max().reset_index()
    grp = so_summary.merge(so_dates, on="SO Number", how="left")

    # ── Final KPI Columns ──
    grp["Sales_Value_FG"]   = grp["Good_Units"]   * grp["Unit_Price"]
    grp["Production_Value"] = grp["Production_Qty"] * grp["Unit_Price"]
    grp["Revenue_Lost"]     = grp["Rejection_Qty"] * grp["Unit_Price"]
    grp["Yield_Rate"]       = (grp["Good_Units"] / grp["Production_Qty"].replace(0, 1)) * 100
    grp["Variance"]         = grp["Production_Qty"] - grp["Target_Qty"]

    return grp

# ─── DEMO DATA GENERATOR ────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def generate_demo_data() -> pd.DataFrame:
    """
    Fallback demo data when Google Sheets is not yet configured.
    Remove this function once live sheet is connected.
    """
    import numpy as np
    rng = np.random.default_rng(42)

    models    = ["Model-A200", "Model-B350", "Model-C150", "Model-X500", "Model-D275"]
    shifts    = ["Morning", "Afternoon", "Night"]
    reasons   = ["Machine Breakdown", "Material Shortage", "Power Outage",
                 "Maintenance", "Operator Absence", "Quality Hold", "None"]
    prices    = {"Model-A200": 4500, "Model-B350": 7800, "Model-C150": 3200,
                 "Model-X500": 12500, "Model-D275": 6100}
    targets   = {"Model-A200": 120, "Model-B350": 90, "Model-C150": 150,
                 "Model-X500": 60, "Model-D275": 100}

    rows = []
    for d in pd.date_range(end=datetime.today(), periods=60, freq="D"):
        for _ in range(rng.integers(3, 8)):
            model   = rng.choice(models)
            shift   = rng.choice(shifts)
            prod    = int(targets[model] * rng.uniform(0.75, 1.15))
            rej     = int(prod * rng.uniform(0.01, 0.10))
            down    = int(rng.choice([0, 0, 0, 15, 30, 45, 60, 90]))
            reason  = "None" if down == 0 else rng.choice(reasons[:-1])
            rows.append({
                "Date":           d,
                "Shift":          shift,
                "Model_Name":     model,
                "Production_Qty": prod,
                "Rejection_Qty":  rej,
                "Target_Qty":     targets[model],
                "Unit_Price":     prices[model],
                "Downtime_Minutes": down,
                "Downtime_Reason":  reason,
                "_source_sheet":  "Demo",
            })

    df = pd.DataFrame(rows)
    df["Good_Units"]       = df["Production_Qty"] - df["Rejection_Qty"]
    df["Sales_Value_FG"]   = df["Good_Units"] * df["Unit_Price"]
    df["Production_Value"] = df["Production_Qty"] * df["Unit_Price"]
    df["Revenue_Lost"]     = df["Rejection_Qty"] * df["Unit_Price"]
    df["Yield_Rate"]       = (df["Good_Units"] / df["Production_Qty"].replace(0, 1)) * 100
    df["Variance"]         = df["Production_Qty"] - df["Target_Qty"]
    return df

# ─── CHART THEME ────────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#8899bb", size=11),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,212,255,0.2)", borderwidth=1),
    colorway=["#00d4ff","#ffb800","#00e676","#ff3d5a","#a78bfa","#ff6e40","#40c4ff"],
)
GRID_STYLE = dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)")

def fmt_currency(val: float) -> str:
    if val >= 1_00_00_000:  return f"₹{val/1_00_00_000:.2f} Cr"
    if val >= 1_00_000:     return f"₹{val/1_00_000:.2f} L"
    return f"₹{val:,.0f}"

# ─── CHART BUILDERS ─────────────────────────────────────────────────────────────
def chart_gauge(yield_rate: float) -> go.Figure:
    color = "#00e676" if yield_rate >= 95 else ("#ffb800" if yield_rate >= 90 else "#ff3d5a")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=yield_rate,
        delta={"reference": 95, "increasing": {"color": "#00e676"}, "decreasing": {"color": "#ff3d5a"}},
        title={"text": "YIELD & QUALITY RATE", "font": {"size": 12, "color": "#8899bb"}},
        number={"suffix": "%", "font": {"size": 36, "color": color, "family": "Bebas Neue"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#8899bb",
                     "tickfont": {"size": 9}, "dtick": 10},
            "bar":  {"color": color, "thickness": 0.28},
            "bgcolor": "rgba(255,255,255,0.03)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 90],   "color": "rgba(255,61,90,0.12)"},
                {"range": [90, 95],  "color": "rgba(255,184,0,0.12)"},
                {"range": [95, 100], "color": "rgba(0,230,118,0.12)"},
            ],
            "threshold": {
                "line": {"color": "#00d4ff", "width": 2},
                "thickness": 0.8, "value": 95,
            },
        },
    ))
    fig.update_layout(**CHART_LAYOUT, height=260)
    return fig

def chart_treemap(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby("Model_Name").agg(
        Revenue=("Sales_Value_FG", "sum"),
        Units=("Good_Units", "sum"),
    ).reset_index()
    fig = px.treemap(
        grp, path=["Model_Name"], values="Revenue",
        color="Revenue",
        color_continuous_scale=[[0,"#0d1526"],[0.5,"#003d55"],[1,"#00d4ff"]],
        hover_data={"Units": True},
        custom_data=["Revenue", "Units"],
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Revenue: %{customdata[0]:,.0f} ₹<br>Units: %{customdata[1]:,}<extra></extra>",
        texttemplate="<b>%{label}</b><br>%{customdata[0]:,.0f} ₹<br>%{customdata[1]:,} units",
        textfont=dict(family="DM Sans", size=11),
        marker=dict(line=dict(color="#0a0e1a", width=2)),
    )
    fig.update_layout(**CHART_LAYOUT, title="MODEL-WISE REVENUE CONTRIBUTION",
                      title_font=dict(size=11, color="#8899bb"), height=340,
                      coloraxis_showscale=False)
    return fig

def chart_variance_bar(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby("Model_Name").agg(
        Actual=("Production_Qty", "sum"),
        Target=("Target_Qty", "sum"),
    ).reset_index()
    grp["Shortfall"] = grp["Actual"] < grp["Target"]
    bar_colors = ["#ff3d5a" if s else "#00d4ff" for s in grp["Shortfall"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Target", x=grp["Model_Name"], y=grp["Target"],
        marker=dict(color="rgba(167,139,250,0.35)", line=dict(color="#a78bfa", width=1.5)),
    ))
    fig.add_trace(go.Bar(
        name="Actual", x=grp["Model_Name"], y=grp["Actual"],
        marker=dict(color=bar_colors),
        text=[f"{'▼' if s else '▲'} {abs(a-t):,}" for s, a, t in
              zip(grp["Shortfall"], grp["Actual"], grp["Target"])],
        textposition="outside",
        textfont=dict(color=["#ff3d5a" if s else "#00e676" for s in grp["Shortfall"]], size=10),
    ))
    fig.update_layout(**CHART_LAYOUT, title="TARGET vs ACTUAL PRODUCTION",
                      title_font=dict(size=11, color="#8899bb"),
                      barmode="group", height=320,
                      xaxis=dict(title="", **GRID_STYLE),
                      yaxis=dict(title="Units", **GRID_STYLE))
    return fig

def chart_pareto_downtime(df: pd.DataFrame) -> go.Figure:
    dtdf = df[df["Downtime_Reason"] != "None"].copy()
    if dtdf.empty:
        return None
    grp = dtdf.groupby("Downtime_Reason").agg(
        Minutes=("Downtime_Minutes", "sum"),
        Loss=("Revenue_Lost", "sum"),
    ).sort_values("Minutes", ascending=False).reset_index()
    grp["Cumulative_%"] = (grp["Minutes"].cumsum() / grp["Minutes"].sum() * 100).round(1)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=grp["Downtime_Reason"], y=grp["Minutes"],
        name="Downtime (min)", marker_color="#ff3d5a",
        text=grp["Loss"].apply(fmt_currency),
        textposition="outside", textfont=dict(color="#ffb800", size=9),
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=grp["Downtime_Reason"], y=grp["Cumulative_%"],
        name="Cumulative %", mode="lines+markers",
        line=dict(color="#00d4ff", width=2),
        marker=dict(color="#00d4ff", size=6),
    ), secondary_y=True)

    fig.add_hline(y=80, line_dash="dot", line_color="#ffb800",
                  annotation_text="80% Pareto", annotation_font_color="#ffb800",
                  secondary_y=True)
    fig.update_layout(**CHART_LAYOUT, title="DOWNTIME PARETO ANALYSIS (with Revenue Impact)",
                      title_font=dict(size=11, color="#8899bb"), height=340)
    fig.update_yaxes(title_text="Downtime (min)", secondary_y=False, **GRID_STYLE)
    fig.update_yaxes(title_text="Cumulative %", range=[0, 105], secondary_y=True, **GRID_STYLE)
    return fig

def chart_daily_trend(df: pd.DataFrame) -> go.Figure:
    daily = df.groupby("Date").agg(
        Sales=("Sales_Value_FG", "sum"),
        Loss=("Revenue_Lost", "sum"),
    ).reset_index().sort_values("Date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Sales"],
        name="Sales Value (FG)", mode="lines",
        line=dict(color="#00d4ff", width=2.5),
        fill="tozeroy", fillcolor="rgba(0,212,255,0.06)",
    ))
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Loss"],
        name="Revenue Lost", mode="lines",
        line=dict(color="#ff3d5a", width=1.8, dash="dot"),
    ))
    fig.update_layout(**CHART_LAYOUT, title="DAILY REVENUE TREND",
                      title_font=dict(size=11, color="#8899bb"), height=280,
                      xaxis=dict(title="", **GRID_STYLE),
                      yaxis=dict(title="₹ Value", **GRID_STYLE))
    return fig

def chart_shift_heatmap(df: pd.DataFrame) -> go.Figure:
    pivot = df.pivot_table(index="Model_Name", columns="Shift",
                           values="Yield_Rate", aggfunc="mean").fillna(0)
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale=[[0,"#ff3d5a"],[0.5,"#ffb800"],[1,"#00e676"]],
        zmin=80, zmax=100,
        text=[[f"{v:.1f}%" for v in row] for row in pivot.values],
        texttemplate="%{text}", textfont=dict(size=11, color="#0a0e1a"),
        colorbar=dict(title="Yield%", tickfont=dict(color="#8899bb")),
    ))
    fig.update_layout(**CHART_LAYOUT, title="YIELD RATE HEATMAP (Model × Shift)",
                      title_font=dict(size=11, color="#8899bb"), height=300)
    return fig

def chart_coq_bar(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby("Model_Name").agg(
        Revenue_Lost=("Revenue_Lost", "sum"),
        Rejection_Qty=("Rejection_Qty", "sum"),
    ).sort_values("Revenue_Lost", ascending=True).reset_index()

    fig = go.Figure(go.Bar(
        y=grp["Model_Name"],
        x=grp["Revenue_Lost"],
        orientation="h",
        marker=dict(
            color=grp["Revenue_Lost"],
            colorscale=[[0,"#ffb800"],[1,"#ff3d5a"]],
            showscale=False,
        ),
        text=[f"{fmt_currency(v)}  ({int(r)} units)"
              for v, r in zip(grp["Revenue_Lost"], grp["Rejection_Qty"])],
        textposition="outside",
        textfont=dict(color="#ffb800", size=10),
    ))
    fig.update_layout(**CHART_LAYOUT, title="COST OF QUALITY — REVENUE LOST BY MODEL",
                      title_font=dict(size=11, color="#8899bb"), height=300,
                      xaxis=dict(title="₹ Revenue Lost", **GRID_STYLE),
                      yaxis=dict(title="", **GRID_STYLE))
    return fig

# ─── PDF EXPORT ─────────────────────────────────────────────────────────────────
def generate_pdf_report(df: pd.DataFrame, kpis: dict) -> bytes:
    """Generates a simple HTML → PDF byte string using weasyprint (if installed)."""
    date_from = df["Date"].min().strftime("%d %b") if not df.empty else "N/A"
    date_to = df["Date"].max().strftime("%d %b %Y") if not df.empty else "N/A"
    cols = ['Date','Shift','Model_Name','Production_Qty','Rejection_Qty','Good_Units','Yield_Rate','Sales_Value_FG','Revenue_Lost']
    rename_map = {'Production_Qty':'Prod Qty','Rejection_Qty':'Rej Qty','Good_Units':'Good Units','Yield_Rate':'Yield %','Sales_Value_FG':'Sales ₹','Revenue_Lost':'Lost ₹'}
    table_html = df.tail(20)[cols].rename(columns=rename_map).to_html(index=False, float_format=lambda x: f"{x:,.1f}")
    html_content = f"""
    <html><head><meta charset='utf-8'>
    <style>
      body {{ font-family: Arial, sans-serif; background: #fff; color: #222; margin: 2cm; }}
      h1 {{ color: #003d55; border-bottom: 3px solid #00d4ff; padding-bottom: 8px; }}
      h2 {{ color: #005577; font-size: 1rem; margin-top: 1.5rem; }}
      .kpi-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:1rem 0; }}
      .kpi {{ background:#f0f8ff; border-radius:8px; padding:12px; border-left:4px solid #00d4ff; }}
      .kpi-val {{ font-size:1.5rem; font-weight:700; color:#003d55; }}
      .kpi-lbl {{ font-size:0.75rem; color:#556; text-transform:uppercase; }}
      table {{ width:100%; border-collapse:collapse; margin-top:1rem; }}
      th {{ background:#003d55; color:#fff; padding:8px; font-size:0.8rem; text-transform:uppercase; }}
      td {{ padding:6px 8px; border-bottom:1px solid #dde; font-size:0.82rem; }}
      tr:nth-child(even) {{ background:#f8fbff; }}
      .footer {{ margin-top:2rem; font-size:0.75rem; color:#888; text-align:center; }}
    </style></head><body>
    <h1>🏭 Spar Appliancesuring MD Strategic Report</h1>
    <p><b>Generated:</b> {datetime.now(timezone(timedelta(hours=5,minutes=30))).strftime('%d %B %Y, %H:%M')} &nbsp;|&nbsp;
       <b>Period:</b> {date_from} - {date_to}</p>

    <h2>KEY PERFORMANCE INDICATORS</h2>
    <div class='kpi-grid'>
      <div class='kpi'><div class='kpi-lbl'>Total Sales Value (FG)</div>
        <div class='kpi-val'>{fmt_currency(kpis.get('sales',0))}</div></div>
      <div class='kpi'><div class='kpi-lbl'>Total Production Value</div>
        <div class='kpi-val'>{fmt_currency(kpis.get('prod_value',0))}</div></div>
      <div class='kpi'><div class='kpi-lbl'>Yield Rate</div>
        <div class='kpi-val'>{kpis.get('yield',0):.1f}%</div></div>
      <div class='kpi'><div class='kpi-lbl'>Revenue Lost (CoQ)</div>
        <div class='kpi-val'>{fmt_currency(kpis.get('loss',0))}</div></div>
      <div class='kpi'><div class='kpi-lbl'>Total Downtime</div>
        <div class='kpi-val'>{kpis.get('downtime',0):,} min</div></div>
      <div class='kpi'><div class='kpi-lbl'>Total Units Produced</div>
        <div class='kpi-val'>{kpis.get('units',0):,}</div></div>
    </div>

    <h2>PRODUCTION DETAIL (Last 20 Records)</h2>
    {table_html}

    <div class='footer'>Confidential — MD Strategic Dashboard | Auto-generated Report</div>
    </body></html>
    """
    try:
        import weasyprint
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        return pdf_bytes
    except ImportError:
        # Fallback: return HTML if weasyprint not available
        return html_content.encode("utf-8")

# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
def render_sidebar(df_raw: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        # User info
        st.markdown(f"""
        <div style="background:rgba(0,212,255,0.07);border:1px solid rgba(0,212,255,0.2);
                    border-radius:10px;padding:0.9rem;margin-bottom:1rem;">
          <div style="font-size:0.7rem;color:#8899bb;text-transform:uppercase;letter-spacing:1px;">Logged in as</div>
          <div style="font-size:1rem;font-weight:600;color:#00d4ff;margin-top:0.2rem;">
            👤 {st.session_state.get('username','')}</div>
          <div style="font-size:0.72rem;color:#a78bfa;">{st.session_state.get('role','')}</div>
          <div style="font-size:0.72rem;color:#00d4ff;margin-top:0.2rem;">MD: Mr. Abhimanyu Dua</div>
          <div style="font-size:0.68rem;color:#556677;margin-top:0.3rem;">
            Since {st.session_state.get('login_time','')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Live status
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:1.2rem;">
          <div class="pulse-dot"></div>
          <span style="font-size:0.72rem;color:#00e676;text-transform:uppercase;
                       letter-spacing:1px;font-weight:600;">LIVE DATA FEED</span>
        </div>
        """, unsafe_allow_html=True)

        # Archive toggle
        st.markdown('<div class="sidebar-section">📁 Data Source</div>', unsafe_allow_html=True)
        include_archives = st.toggle("Include Historical Archives", value=False)

        # Date range
        st.markdown('<div class="sidebar-section">📅 Date Range</div>', unsafe_allow_html=True)
        if not df_raw.empty and "Date" in df_raw.columns:
            min_d = df_raw["Date"].min().date()
            max_d = df_raw["Date"].max().date()
        else:
            min_d = (datetime.today() - timedelta(days=30)).date()
            max_d = datetime.today().date()

        date_start = st.date_input("From", value=min_d, min_value=min_d, max_value=max_d)
        date_end   = st.date_input("To",   value=max_d, min_value=min_d, max_value=max_d)

        # Model filter
        st.markdown('<div class="sidebar-section">🏷️ Model</div>', unsafe_allow_html=True)
        all_models = sorted(df_raw["Model_Name"].dropna().unique()) if not df_raw.empty else []
        sel_models = st.multiselect("Models", all_models, default=all_models)

        # Shift filter
        st.markdown('<div class="sidebar-section">⏱️ Shift</div>', unsafe_allow_html=True)
        all_shifts = sorted(df_raw["Shift"].dropna().unique()) if not df_raw.empty else []
        sel_shifts = st.multiselect("Shifts", all_shifts, default=all_shifts)

        # Apply filters
        df = df_raw.copy()
        if "Date" in df.columns:
            df = df[(df["Date"].dt.date >= date_start) & (df["Date"].dt.date <= date_end)]
        if sel_models:
            df = df[df["Model_Name"].isin(sel_models)]
        if sel_shifts:
            df = df[df["Shift"].isin(sel_shifts)]

        # Export
        st.markdown('<div class="sidebar-section">📤 Export</div>', unsafe_allow_html=True)
        if st.button("⬇️  Download CSV"):
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📄 Save CSV", csv, "md_dashboard_export.csv", "text/csv")

        if st.button("🖨️ PDF Report"):
            kpis = {
                "sales":      df["Sales_Value_FG"].sum(),
                "prod_value": df["Production_Value"].sum(),
                "yield":      (df["Good_Units"].sum() / max(df["Production_Qty"].sum(), 1)) * 100,
                "loss":       df["Revenue_Lost"].sum(),
                "downtime":   int(df["Downtime_Minutes"].sum()),
                "units":      int(df["Production_Qty"].sum()),
            }
            pdf = generate_pdf_report(df, kpis)
            ext  = "pdf" if pdf[:4] == b'%PDF' else "html"
            mime = "application/pdf" if ext == "pdf" else "text/html"
            st.download_button("💾 Save Report", pdf, f"md_report_{datetime.now(timezone(timedelta(hours=5,minutes=30))).strftime('%Y%m%d_%H%M')}.{ext}", mime)

        # Logout
        st.markdown("---")
        if st.button("🚪  Logout"):
            for key in ["authenticated","username","role","login_time"]:
                st.session_state.pop(key, None)
            st.rerun()

        return df, include_archives

# ─── ALERTS ─────────────────────────────────────────────────────────────────────
def render_alerts(df: pd.DataFrame):
    if df.empty:
        return
    yield_rate  = (df["Good_Units"].sum() / max(df["Production_Qty"].sum(), 1)) * 100
    total_down  = df["Downtime_Minutes"].sum()
    shortfall_models = df.groupby("Model_Name").apply(
        lambda x: (
            x["Target_Qty"].sum() > 0 and
            (x["Production_Qty"].sum() / x["Target_Qty"].sum()) < 0.20
        )
    )
    shortfalls = shortfall_models[shortfall_models].index.tolist()

    alert_shown = False
    if yield_rate < 90:
        st.markdown(f"""<div class="alert-critical">
          <span class="alert-icon">🚨</span>
          <span class="alert-text"><b>CRITICAL:</b> Yield Rate is <b>{yield_rate:.1f}%</b> — 
          well below the 95% threshold. Immediate quality intervention required.</span>
        </div>""", unsafe_allow_html=True)
        alert_shown = True
    elif yield_rate < 95:
        st.markdown(f"""<div class="alert-warning">
          <span class="alert-icon">⚠️</span>
          <span class="alert-text"><b>WARNING:</b> Yield Rate is <b>{yield_rate:.1f}%</b> — 
          below the 95% threshold. Review rejection causes.</span>
        </div>""", unsafe_allow_html=True)
        alert_shown = True

    if total_down > 500:
        st.markdown(f"""<div class="alert-critical">
          <span class="alert-icon">🔴</span>
          <span class="alert-text"><b>EXCESSIVE DOWNTIME:</b> Total downtime is 
          <b>{total_down:,} minutes ({total_down/60:.1f} hrs)</b> in selected period.</span>
        </div>""", unsafe_allow_html=True)
        alert_shown = True
    elif total_down > 200:
        st.markdown(f"""<div class="alert-warning">
          <span class="alert-icon">🟡</span>
          <span class="alert-text"><b>HIGH DOWNTIME:</b> <b>{total_down:,} minutes</b> recorded. 
          Review Pareto analysis below.</span>
        </div>""", unsafe_allow_html=True)
        alert_shown = True

    if shortfalls:
        st.markdown(f"""<div class="alert-warning">
          <span class="alert-icon">📉</span>
          <span class="alert-text"><b>PRODUCTION SHORTFALL:</b> Models below target — 
          <b>{', '.join(shortfalls)}</b></span>
        </div>""", unsafe_allow_html=True)
        alert_shown = True

    if not alert_shown:
        st.markdown("""<div class="alert-ok">
          ✅ &nbsp;<b>All systems normal.</b> Yield, downtime, and production are within targets.
        </div>""", unsafe_allow_html=True)

# ─── MAIN DASHBOARD ─────────────────────────────────────────────────────────────
def render_dashboard():
    # ── Load Material Icons Font ──
    st.markdown("""
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
    .material-icons, [data-testid="collapsedControl"] * {
        font-family: 'Material Icons' !important;
        font-feature-settings: 'liga';
        -webkit-font-feature-settings: 'liga';
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Top Bar ──
    now = datetime.now()
    st.markdown(f"""
    <div class="topbar">
      <div>
        <div class="topbar-logo" style="display:flex;align-items:center;gap:10px;"><img src="data:image/png;base64,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" style="height:45px;width:45px;object-fit:contain;border-radius:6px;"/> SPAR APPLIANCES</div>
        <div class="topbar-sub">MD Strategic Dashboard &nbsp;·&nbsp; Real-Time Intelligence</div>
      </div>
      <div style="display:flex;align-items:center;gap:1rem;">
        <div class="status-live">
          <div class="pulse-dot"></div>LIVE
        </div>
        <div class="topbar-time">{now.strftime('%d %b %Y &nbsp;|&nbsp; %H:%M:%S')}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)



    # ── Load Data ──
    is_live = SPREADSHEET_ID != "YOUR_SPREADSHEET_ID_HERE"
    if is_live:
        df_raw = fetch_all_data(include_archives=False)
        if df_raw.empty:
            st.warning("⚠️ Live sheet returned no data. Falling back to demo data.")
            df_raw = generate_demo_data()
        else:
            st.sidebar.success("✅ Connected to Google Sheets")
    else:
        df_raw = generate_demo_data()
        st.sidebar.info("ℹ️ Demo mode — Set SPREADSHEET_ID to connect live Spar Appliances sheet.")

    # ── Sidebar Filters ──
    df, include_archives = render_sidebar(df_raw)
    if include_archives and is_live:
        df_raw = fetch_all_data(include_archives=True)
        df = df_raw.copy()

    if df.empty:
        st.error("No data available for the selected filters.")
        return

    # ── Compute KPIs ──
    total_sales     = df["Sales_Value_FG"].sum()
    total_prod_val  = df["Production_Value"].sum()
    total_loss      = df["Revenue_Lost"].sum()
    total_units     = int(df["Production_Qty"].sum())
    good_units      = int(df["Good_Units"].sum())
    total_rej       = int(df["Rejection_Qty"].sum())
    yield_rate      = (good_units / max(total_units, 1)) * 100
    total_downtime  = int(df["Downtime_Minutes"].sum())
    total_target    = int(df["Target_Qty"].sum())
    overall_var     = total_units - total_target
    var_pct         = (overall_var / max(total_target, 1)) * 100

    # ── Alerts ──
    render_alerts(df)

    # ── KPI Row ──
    st.markdown('<div class="section-title">📊 Core Financial & Production KPIs</div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    def kpi_card(col, label, value, delta_text, delta_positive, icon):
        delta_class = "positive" if delta_positive else "negative"
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-delta {delta_class}">{delta_text}</div>
          <div class="kpi-icon">{icon}</div>
        </div>""", unsafe_allow_html=True)

    kpi_card(k1, "Sales Value (FG)",     fmt_currency(total_sales),    f"Net after rejections", True,  "💰")
    kpi_card(k2, "Total Production Val", fmt_currency(total_prod_val), f"Gross output value",   True,  "🏭")
    kpi_card(k3, "Yield Rate",           f"{yield_rate:.1f}%",         f"{'▲' if yield_rate>=95 else '▼'} Target: 95%", yield_rate>=95, "📈")
    kpi_card(k4, "Revenue Lost (CoQ)",   fmt_currency(total_loss),     f"{total_rej:,} units rejected", False, "📉")
    kpi_card(k5, "Variance vs Target",   f"{overall_var:+,} u",        f"{var_pct:+.1f}% of target", overall_var>=0, "🎯")
    kpi_card(k6, "Total Downtime",       f"{total_downtime:,} min",    f"= {total_downtime/60:.1f} hrs", total_downtime<200, "⏱️")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Gauge + Treemap ──
    st.markdown('<div class="section-title">🎯 Quality & Revenue Distribution</div>', unsafe_allow_html=True)
    col_g, col_t = st.columns([1, 2])
    with col_g:
        st.plotly_chart(chart_gauge(yield_rate), use_container_width=True, config={"displayModeBar": False})
    with col_t:
        st.plotly_chart(chart_treemap(df), use_container_width=True, config={"displayModeBar": False})

    # ── Row 3: Variance Bar + Daily Trend ──
    st.markdown('<div class="section-title">📦 Production Performance</div>', unsafe_allow_html=True)
    col_v, col_d = st.columns([1, 1])
    with col_v:
        st.plotly_chart(chart_variance_bar(df), use_container_width=True, config={"displayModeBar": False})
    with col_d:
        st.plotly_chart(chart_daily_trend(df), use_container_width=True, config={"displayModeBar": False})

    # ── Row 4: Pareto + CoQ ──
    st.markdown('<div class="section-title">⚙️ Downtime & Cost of Quality Analysis</div>', unsafe_allow_html=True)
    col_p, col_c = st.columns([1, 1])
    with col_p:
        pareto = chart_pareto_downtime(df)
        if pareto:
            st.plotly_chart(pareto, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No downtime events recorded for this period.")
    with col_c:
        st.plotly_chart(chart_coq_bar(df), use_container_width=True, config={"displayModeBar": False})

    # ── Row 5: Heatmap ──
    st.markdown('<div class="section-title">🌡️ Shift-wise Yield Heatmap</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_shift_heatmap(df), use_container_width=True, config={"displayModeBar": False})

    # ── Row 6: Raw Data Table ──
    st.markdown('<div class="section-title">📋 Live Production Records</div>', unsafe_allow_html=True)
    show_table = st.checkbox("Show Detailed Production Log")
    if show_table:
        display_cols = ["Date","Shift","Model_Name","Production_Qty","Rejection_Qty",
                        "Good_Units","Yield_Rate","Target_Qty","Variance",
                        "Sales_Value_FG","Revenue_Lost","Downtime_Minutes","Downtime_Reason"]
        show_df = df[display_cols].copy()
        show_df["Date"] = show_df["Date"].dt.strftime("%d %b %Y")
        show_df["Yield_Rate"] = show_df["Yield_Rate"].round(1)
        show_df["Sales_Value_FG"] = show_df["Sales_Value_FG"].apply(fmt_currency)
        show_df["Revenue_Lost"]   = show_df["Revenue_Lost"].apply(fmt_currency)
        st.dataframe(show_df, use_container_width=True, height=380)

    # ── Auto-refresh countdown ──
    st.markdown(f"""
    <div style="text-align:center;padding:1rem 0 0;font-size:0.7rem;color:#445577;">
      ⟳ &nbsp;Data auto-refreshes every <b>10 minutes</b> &nbsp;|&nbsp;
      Last loaded: <b>{now.strftime('%H:%M:%S')}</b> &nbsp;|&nbsp;
      Next refresh: <b>{(now + timedelta(minutes=10)).strftime('%H:%M')}</b>
    </div>""", unsafe_allow_html=True)

    # Auto-refresh trigger (every 600 seconds)
    time.sleep(0)
    st.markdown("""
    <script>
      setTimeout(function(){ window.location.reload(); }, 600000);
    </script>""", unsafe_allow_html=True)

# ─── ENTRY POINT ────────────────────────────────────────────────────────────────
def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        login_screen()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
