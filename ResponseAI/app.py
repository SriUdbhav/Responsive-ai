"""
AI Research Command Center
---------------------------
Streamlit front-end for the multi-agent research pipeline.
Includes:
- Original dark and light research-lab aesthetic
- Voice Assistant: Voice query input (Speech-to-Text) + Voice report playback (Text-to-Speech)
- Theme Toggle: Dark Theme & Light Theme
- Top Navigation Bar: Multi-language translator for English, Hindi, Telugu, Japanese
"""

import time
import json
import re
import html as html_lib
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# Ensure ResponseAI directory is on sys.path
_current_dir = Path(__file__).resolve().parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

from translator import (
    LANGUAGES,
    LANGUAGE_LIST,
    get_ui_text,
    translate_text,
    translate_query_to_english,
)
from voice_components import render_voice_input_card, render_voice_player_card

# ------------------------------------------------------------------
# Import the REAL pipeline.
# ------------------------------------------------------------------
IMPORT_ERROR = None
try:
    from pipeline import research_pipeline
except Exception as e:  # noqa: BLE001
    IMPORT_ERROR = str(e)


# ====================================================================
# PAGE CONFIG
# ====================================================================
st.set_page_config(
    page_title="Research Command Center",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ====================================================================
# SESSION STATE & PERSISTENT CHAT HISTORY
# ====================================================================
HISTORY_FILE = Path(__file__).resolve().parent / "chat_history.json"


def load_chat_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []


def save_chat_history(history_list):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_list, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"
if "history" not in st.session_state:
    st.session_state.history = load_chat_history()
if "topic_input" not in st.session_state:
    st.session_state.topic_input = ""
if "auto_run" not in st.session_state:
    st.session_state.auto_run = False
if "form_nonce" not in st.session_state:
    st.session_state.form_nonce = 0
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None
if "current" not in st.session_state:
    # Automatically open the last chat into the main screen if history exists
    st.session_state.current = st.session_state.history[-1] if st.session_state.history else None
if "translations" not in st.session_state:
    st.session_state.translations = {}

cur_lang = st.session_state.selected_language
cur_theme = st.session_state.theme


# ====================================================================
# SAFE HTML & CSS RENDERING (Uses st.html so CSS never renders as text)
# ====================================================================
def H(raw_html):
    if hasattr(st, "html"):
        st.html(str(raw_html))
    else:
        cleaned = "\n".join(line.strip() for line in str(raw_html).strip().split("\n") if line.strip())
        st.markdown(cleaned, unsafe_allow_html=True)


def get_css_vars(theme: str) -> str:
    if theme == "light":
        return """
:root{
--bg-0:#F4F6F9;
--bg-1:#E9EEF5;
--bg-panel:#FFFFFF;
--bg-card:#F8FAFC;
--border:#DDE3EA;
--border-bright:#CBD5E1;
--text-hi:#0F172A;
--text-mid:#475569;
--text-lo:#64748B;
--cyan:#0284C7;
--cyan-dim:rgba(2,132,199,0.12);
--amber:#D97706;
--violet:#7C3AED;
--rose:#E11D48;
--green:#16A34A;
--btn-submit-bg:#0284C7;
--btn-submit-hover:#0369A1;
--btn-submit-text:#FFFFFF;
--mono:'JetBrains Mono', monospace;
--sans:'Inter', sans-serif;
--display:'Space Grotesk', sans-serif;
}
.stApp{
background:
radial-gradient(circle at 15% 0%, rgba(2,132,199,0.05), transparent 40%),
radial-gradient(circle at 85% 15%, rgba(124,58,237,0.04), transparent 45%),
var(--bg-0);
color: var(--text-hi);
}
"""
    else:
        return """
:root{
--bg-0:#080B10;
--bg-1:#0D131C;
--bg-panel:#111926;
--bg-card:#141D2C;
--border:#212C3D;
--border-bright:#324361;
--text-hi:#E9EEF6;
--text-mid:#9BA8BE;
--text-lo:#5B677D;
--cyan:#4FE8D3;
--cyan-dim:rgba(79,232,211,0.14);
--amber:#F5A93F;
--violet:#9B87F5;
--rose:#F5677D;
--green:#4ADE80;
--btn-submit-bg:#4FE8D3;
--btn-submit-hover:#3CD6C2;
--btn-submit-text:#04110E;
--mono:'JetBrains Mono', monospace;
--sans:'Inter', sans-serif;
--display:'Space Grotesk', sans-serif;
}
.stApp{
background:
radial-gradient(circle at 15% 0%, rgba(79,232,211,0.06), transparent 40%),
radial-gradient(circle at 85% 15%, rgba(155,135,245,0.05), transparent 45%),
var(--bg-0);
color: var(--text-hi);
}
"""


CORE_STYLES = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"]{ font-family: var(--sans); }
#MainMenu, footer, [data-testid="stDeployButton"]{visibility:hidden !important; display:none !important;}
header[data-testid="stHeader"]{background:transparent !important; z-index:9999 !important;}
[data-testid="stToolbar"]{visibility:visible !important; display:flex !important;}
[data-testid="stExpandSidebarButton"]{
visibility:visible !important;
display:inline-flex !important;
opacity:1 !important;
background:var(--bg-panel) !important;
border:1.5px solid var(--cyan) !important;
border-radius:8px !important;
color:var(--cyan) !important;
padding:4px 8px !important;
cursor:pointer !important;
box-shadow:0 4px 14px rgba(0,0,0,0.4) !important;
z-index:999999 !important;
}
[data-testid="stExpandSidebarButton"] svg{
fill:var(--cyan) !important;
color:var(--cyan) !important;
}
[data-testid="stSidebarCollapseButton"]{
visibility:visible !important;
display:inline-flex !important;
color:var(--cyan) !important;
}
.block-container{padding-top:1.2rem; max-width:1180px;}
::-webkit-scrollbar{width:8px; height:8px;}
::-webkit-scrollbar-track{background:var(--bg-0);}
::-webkit-scrollbar-thumb{background:var(--border-bright); border-radius:4px;}
section[data-testid="stSidebar"]{
background: linear-gradient(180deg, var(--bg-1), var(--bg-0)) !important;
border-right:1px solid var(--border) !important;
overflow-x:hidden !important;
}
section[data-testid="stSidebar"] .block-container{padding-top:1.4rem;}
.brand-mark{
display:flex; align-items:center; gap:12px; margin-bottom:14px;
padding-bottom:12px; border-bottom:1px solid var(--border);
}
.brand-glyph{
width:36px; height:36px; border-radius:10px;
background:linear-gradient(135deg, var(--cyan), var(--violet));
display:flex; align-items:center; justify-content:center;
font-family:var(--display); font-weight:700; color:#04110E; font-size:17px;
box-shadow:0 0 12px rgba(79,232,211,0.25);
flex-shrink:0;
}
.brand-text-title{font-family:var(--display); font-weight:700; font-size:15px; color:var(--text-hi); line-height:1.15;}
.brand-text-sub{font-family:var(--mono); font-size:10px; letter-spacing:0.09em; color:var(--text-lo); text-transform:uppercase; margin-top:2px;}
.top-navbar-bar{
display:flex; align-items:center; justify-content:space-between;
background:var(--bg-panel); border:1px solid var(--border); border-radius:14px;
padding:8px 16px; margin-bottom:18px;
}
.side-section-label{
font-family:var(--mono); font-size:10.5px; letter-spacing:0.12em; text-transform:uppercase;
color:var(--text-lo); margin:20px 0 8px 0; border-bottom:1px solid var(--border); padding-bottom:6px;
}
.env-row{display:flex; align-items:center; justify-content:space-between; font-family:var(--mono); font-size:11.5px; padding:4px 0; color:var(--text-mid);}
.dot{width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:8px;}
.dot-ok{background:var(--green); box-shadow:0 0 6px var(--green);}
.dot-bad{background:var(--rose); box-shadow:0 0 6px var(--rose);}
.history-item{
background:var(--bg-card); border:1px solid var(--border); border-radius:10px;
padding:10px 12px; margin-bottom:8px;
}
.history-topic{font-size:12.5px; color:var(--text-hi); font-weight:500; line-height:1.3; margin-bottom:4px;}
.history-meta{font-family:var(--mono); font-size:10px; color:var(--text-lo); display:flex; justify-content:space-between;}
.hero-eyebrow{
font-family:var(--mono); font-size:11.5px; letter-spacing:0.16em; text-transform:uppercase;
color:var(--cyan); display:flex; align-items:center; gap:8px; margin-bottom:10px;
}
.hero-eyebrow::before{content:''; width:7px; height:7px; border-radius:50%; background:var(--cyan); box-shadow:0 0 8px var(--cyan); animation:blink 2s infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0.35;}}
.hero-title{
font-family:var(--display); font-weight:700; font-size:clamp(30px,4vw,44px);
line-height:1.08; letter-spacing:-0.02em; color:var(--text-hi); margin:0 0 10px 0;
}
.hero-title span{
background:linear-gradient(90deg, var(--cyan), var(--violet));
-webkit-background-clip:text; background-clip:text; color:transparent;
}
.hero-sub{color:var(--text-mid); font-size:15px; max-width:640px; line-height:1.55; margin-bottom:24px;}
div[data-testid="stForm"]{
background:var(--bg-panel); border:1px solid var(--border); border-radius:16px;
padding:22px 22px 16px 22px; box-shadow:0 20px 50px -25px rgba(0,0,0,0.6);
}
.stTextInput input{
background:var(--bg-card) !important; color:var(--text-hi) !important;
border:1px solid var(--border-bright) !important; border-radius:10px !important;
font-family:var(--sans) !important; font-size:15px !important; padding:13px 16px !important;
}
.stTextInput input:focus{
border-color:var(--cyan) !important; box-shadow:0 0 0 3px var(--cyan-dim) !important;
}
.stTextInput label{
font-family:var(--mono) !important; font-size:11px !important; letter-spacing:0.08em !important;
text-transform:uppercase; color:var(--text-lo) !important;
}
div[data-testid="stFormSubmitButton"] button{
background:var(--btn-submit-bg) !important;
border:1px solid var(--btn-submit-bg) !important;
border-radius:10px !important;
font-weight:700 !important;
font-family:var(--display) !important;
font-size:14px !important;
letter-spacing:0.01em;
padding:10px 22px !important;
box-shadow:none !important;
transition:background-color 0.15s ease, border-color 0.15s ease !important;
transform:none !important;
white-space:nowrap !important;
min-height:44px !important;
}
div[data-testid="stFormSubmitButton"] button,
div[data-testid="stFormSubmitButton"] button *,
div[data-testid="stFormSubmitButton"] button p{
color:var(--btn-submit-text) !important;
-webkit-text-fill-color:var(--btn-submit-text) !important;
font-weight:700 !important;
font-family:var(--display) !important;
font-size:14px !important;
margin:0 !important;
opacity:1 !important;
text-shadow:none !important;
}
div[data-testid="stFormSubmitButton"] button:hover{
background:var(--btn-submit-hover) !important;
border-color:var(--btn-submit-hover) !important;
filter:none !important;
transform:none !important;
box-shadow:none !important;
}
div[data-testid="stFormSubmitButton"] button:active{
filter:brightness(0.92) !important;
transform:none !important;
box-shadow:none !important;
}
.stButton button{
background:var(--bg-card) !important;
color:var(--text-mid) !important;
border:1px solid var(--border) !important;
border-radius:20px !important;
font-size:12.5px !important;
padding:6px 14px !important;
font-family:var(--sans) !important;
box-shadow:none !important;
transform:none !important;
transition:border-color 0.2s ease, color 0.2s ease !important;
}
.stButton button:hover{
border-color:var(--border-bright) !important;
color:var(--text-hi) !important;
background:var(--bg-card) !important;
box-shadow:none !important;
transform:none !important;
}
.stButton button:active{
transform:none !important;
box-shadow:none !important;
}
/* "New Research" Action Button (First button in sidebar) */
section[data-testid="stSidebar"] div[data-testid="stButton"]:first-of-type button{
background:var(--cyan-dim) !important;
border:1px solid var(--cyan) !important;
border-radius:12px !important;
color:var(--cyan) !important;
font-family:var(--display) !important;
font-weight:700 !important;
font-size:13.5px !important;
letter-spacing:0.02em !important;
padding:10px 16px !important;
text-align:center !important;
justify-content:center !important;
box-shadow:none !important;
transform:none !important;
margin-bottom:8px !important;
transition:all 0.15s ease !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"]:first-of-type button p{
color:var(--cyan) !important;
font-weight:700 !important;
font-size:13.5px !important;
text-align:center !important;
margin:0 !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"]:first-of-type button:hover{
background:rgba(79,232,211,0.22) !important;
border-color:var(--cyan) !important;
box-shadow:none !important;
transform:none !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"]:first-of-type button:hover p{
color:#FFFFFF !important;
}

/* Chat History Buttons (Cards with Clean Hover) */
section[data-testid="stSidebar"] div[data-testid="stButton"]:not(:first-of-type) button{
background:var(--bg-card) !important;
border:1px solid var(--border) !important;
border-radius:12px !important;
color:var(--text-hi) !important;
font-family:var(--sans) !important;
font-size:12.5px !important;
text-align:left !important;
justify-content:flex-start !important;
padding:10px 14px !important;
margin-bottom:7px !important;
white-space:pre-wrap !important;
line-height:1.4 !important;
box-shadow:none !important;
transform:none !important;
transition:border-color 0.15s ease, background-color 0.15s ease !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"]:not(:first-of-type) button p{
font-family:var(--sans) !important;
font-size:12.5px !important;
line-height:1.4 !important;
margin:0 !important;
color:var(--text-hi) !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"]:not(:first-of-type) button:hover{
border-color:var(--cyan) !important;
background:var(--bg-panel) !important;
box-shadow:none !important;
transform:none !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"]:not(:first-of-type) button:hover p{
color:var(--cyan) !important;
}

/* Active Chat Item */
section[data-testid="stSidebar"] div[data-testid="stButton"]:not(:first-of-type) button[kind="primary"],
section[data-testid="stSidebar"] div[data-testid="stButton"]:not(:first-of-type) button[data-testid="baseButton-primary"],
section[data-testid="stSidebar"] div[data-testid="stButton"]:not(:first-of-type) button[data-testid*="primary"]{
background:var(--cyan-dim) !important;
border:1px solid var(--cyan) !important;
border-left:4px solid var(--cyan) !important;
color:var(--cyan) !important;
font-weight:600 !important;
box-shadow:none !important;
transform:none !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"]:not(:first-of-type) button[kind="primary"] p,
section[data-testid="stSidebar"] div[data-testid="stButton"]:not(:first-of-type) button[data-testid="baseButton-primary"] p,
section[data-testid="stSidebar"] div[data-testid="stButton"]:not(:first-of-type) button[data-testid*="primary"] p{
color:var(--cyan) !important;
font-weight:600 !important;
}
.chip-label{font-family:var(--mono); font-size:10.5px; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-lo); margin:2px 0 10px 0;}
.pipeline-wrap{
background:var(--bg-panel); border:1px solid var(--border); border-radius:16px;
padding:26px 24px 20px 24px; margin:26px 0 8px 0; position:relative; overflow:hidden;
}
.pipeline-wrap::before{
content:''; position:absolute; inset:0;
background-image: linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
background-size:26px 26px; pointer-events:none;
}
.pipeline-head{display:flex; justify-content:space-between; align-items:center; margin-bottom:22px; position:relative;}
.pipeline-title{font-family:var(--display); font-weight:600; font-size:15px; color:var(--text-hi);}
.pipeline-status-tag{
font-family:var(--mono); font-size:10.5px; letter-spacing:0.08em; text-transform:uppercase;
padding:4px 10px; border-radius:6px; border:1px solid var(--border-bright); color:var(--text-mid);
}
.node-row{display:flex; align-items:flex-start; position:relative;}
.node{flex:1; display:flex; flex-direction:column; align-items:center; text-align:center; position:relative; z-index:2;}
.node-badge{
width:56px; height:56px; border-radius:16px; display:flex; align-items:center; justify-content:center;
background:var(--bg-card); border:1.5px solid var(--border-bright); color:var(--text-lo);
transition:all 0.35s ease; margin-bottom:10px;
}
.node-badge svg{width:24px; height:24px;}
.node.pending .node-badge{ color:var(--text-lo); }
.node.active .node-badge{
color:var(--cyan); border-color:var(--cyan); background:var(--cyan-dim);
box-shadow:0 0 0 6px rgba(79,232,211,0.10), 0 0 22px rgba(79,232,211,0.45);
animation:pulse-ring 1.4s ease-in-out infinite;
}
.node.done .node-badge{ color:#04110E; border-color:var(--green); background:var(--green); }
.node.error .node-badge{ color:#1a0508; border-color:var(--rose); background:var(--rose); }
@keyframes pulse-ring{
0%{ box-shadow:0 0 0 4px rgba(79,232,211,0.14), 0 0 16px rgba(79,232,211,0.3); }
50%{ box-shadow:0 0 0 9px rgba(79,232,211,0.05), 0 0 28px rgba(79,232,211,0.55); }
100%{ box-shadow:0 0 0 4px rgba(79,232,211,0.14), 0 0 16px rgba(79,232,211,0.3); }
}
.node-num{font-family:var(--mono); font-size:10px; color:var(--text-lo); letter-spacing:0.1em;}
.node-label{font-family:var(--display); font-weight:600; font-size:13.5px; color:var(--text-hi); margin-top:2px;}
.node-status{font-family:var(--mono); font-size:10.5px; margin-top:5px; letter-spacing:0.03em;}
.node.pending .node-status{color:var(--text-lo);}
.node.active .node-status{color:var(--cyan);}
.node.done .node-status{color:var(--green);}
.node.error .node-status{color:var(--rose);}
.node-time{font-family:var(--mono); font-size:9.5px; color:var(--text-lo); margin-top:2px;}
.connector{
position:absolute; top:28px; height:2px; left:0; right:0; z-index:1;
background:var(--border); margin:0 56px;
}
.connector-fill{
height:100%; background:linear-gradient(90deg, var(--cyan), var(--green)); width:0%;
transition:width 0.6s ease;
}
.overall-bar-track{ width:100%; height:5px; background:var(--bg-card); border-radius:4px; overflow:hidden; margin-top:18px; border:1px solid var(--border); }
.overall-bar-fill{ height:100%; background:linear-gradient(90deg, var(--cyan), var(--violet)); transition:width 0.5s ease; }
.log-line{
font-family:var(--mono); font-size:12px; color:var(--text-mid); padding:3px 0;
border-left:2px solid var(--border); padding-left:10px; margin-left:3px;
}
.log-line.ok{border-left-color:var(--green); color:var(--text-hi);}
.log-line.err{border-left-color:var(--rose); color:var(--rose);}
.log-time{color:var(--text-lo); margin-right:8px;}
.panel{
background:var(--bg-panel); border:1px solid var(--border); border-radius:16px; padding:22px 24px; margin-top:18px;
}
.panel-title{
font-family:var(--display); font-weight:600; font-size:15px; color:var(--text-hi);
display:flex; align-items:center; gap:8px; margin-bottom:14px;
}
.panel-title .tag{
font-family:var(--mono); font-size:10px; color:var(--cyan); border:1px solid var(--cyan); border-radius:5px;
padding:1px 6px; letter-spacing:0.06em;
}
.finding-card{
background:var(--bg-card); border:1px solid var(--border); border-left:3px solid var(--cyan);
border-radius:10px; padding:14px 16px; margin-bottom:10px; font-size:13.6px; color:var(--text-mid); line-height:1.55;
}
.source-card{
background:var(--bg-card); border:1px solid var(--border); border-radius:12px; padding:14px 16px; margin-bottom:10px;
transition:border-color 0.2s ease;
}
.source-card:hover{ border-color:var(--cyan); }
.source-idx{ font-family:var(--mono); font-size:10.5px; color:var(--cyan); }
.source-title{ font-family:var(--sans); font-weight:600; font-size:13.6px; color:var(--text-hi); margin:4px 0 4px 0; }
.source-url{ font-family:var(--mono); font-size:11px; color:var(--text-lo); word-break:break-all; }
.source-url a{ color:var(--text-mid); text-decoration:none; }
.source-url a:hover{ color:var(--cyan); text-decoration:underline; }
.score-wrap{display:flex; align-items:center; gap:18px; margin-bottom:16px;}
.score-num{font-family:var(--display); font-weight:700; font-size:38px; color:var(--cyan); line-height:1;}
.score-of{font-family:var(--mono); font-size:13px; color:var(--text-lo);}
.score-track{flex:1; height:8px; background:var(--bg-card); border-radius:5px; overflow:hidden; border:1px solid var(--border);}
.score-fill{height:100%; background:linear-gradient(90deg, var(--amber), var(--cyan));}
.verdict-box{
font-family:var(--sans); font-style:italic; color:var(--text-hi); font-size:13.8px;
background:var(--cyan-dim); border:1px solid rgba(79,232,211,0.35); border-radius:10px;
padding:12px 16px; margin-top:6px;
}
.stat-strip{ display:flex; gap:14px; margin-bottom:6px; }
.stat-box{
flex:1; background:var(--bg-card); border:1px solid var(--border); border-radius:12px;
padding:14px 16px;
}
.stat-val{font-family:var(--display); font-weight:700; font-size:22px; color:var(--text-hi);}
.stat-lab{font-family:var(--mono); font-size:10px; letter-spacing:0.08em; text-transform:uppercase; color:var(--text-lo); margin-top:2px;}
hr{ border-color:var(--border) !important; }
.stTabs [data-baseweb="tab-list"]{ gap:4px; border-bottom:1px solid var(--border); }
.stTabs [data-baseweb="tab"]{
font-family:var(--mono) !important; font-size:11.5px !important; letter-spacing:0.05em;
text-transform:uppercase; color:var(--text-lo) !important; padding:8px 4px !important;
}
.stTabs [aria-selected="true"]{ color:var(--cyan) !important; border-bottom-color:var(--cyan) !important; }
.streamlit-expanderHeader{
background:var(--bg-card) !important; border:1px solid var(--border) !important; border-radius:10px !important;
font-family:var(--mono) !important; font-size:12px !important; color:var(--text-mid) !important;
}
div[data-testid="stMarkdownContainer"] p{ color:var(--text-mid); }
</style>
<script>
(function autoExpandSidebar() {
  function tryExpand() {
    try {
      const topWin = window.top || window.parent || window;
      const topDoc = topWin.document;
      for (let i = 0; i < topWin.localStorage.length; i++) {
        const k = topWin.localStorage.key(i);
        if (k && (k.indexOf("stSidebarCollapsed") !== -1 || k.indexOf("sidebar") !== -1)) {
          if (topWin.localStorage.getItem(k) === "true") {
            topWin.localStorage.setItem(k, "false");
          }
        }
      }
      const sidebar = topDoc.querySelector('section[data-testid="stSidebar"]') || document.querySelector('section[data-testid="stSidebar"]');
      const expandBtn = topDoc.querySelector('[data-testid="stExpandSidebarButton"]') || 
                        topDoc.querySelector('[data-testid="stSidebarCollapseButton"]') ||
                        document.querySelector('[data-testid="stExpandSidebarButton"]');
      if (sidebar && sidebar.getAttribute("aria-expanded") === "false" && expandBtn) {
        expandBtn.click();
      }
    } catch(e) {}
  }
  tryExpand();
  setTimeout(tryExpand, 100);
  setTimeout(tryExpand, 400);
  setTimeout(tryExpand, 1000);
})();
</script>
"""


# Inject clean CSS
H(f"<style>{get_css_vars(st.session_state.theme)}</style>\n{CORE_STYLES}")


# ====================================================================
# STAGE DEFINITIONS & ICONS
# ====================================================================
STAGES = [
    {"key": "search", "label": "Search", "sub": "Agent 01", "verb": "Scanning the web"},
    {"key": "reader", "label": "Reader", "sub": "Agent 02", "verb": "Reading top source"},
    {"key": "writer", "label": "Writer", "sub": "Agent 03", "verb": "Drafting report"},
    {"key": "critic", "label": "Critic", "sub": "Agent 04", "verb": "Reviewing report"},
]

EXAMPLE_QUERIES = [
    "Latest breakthroughs in solid-state EV batteries in 2026",
    "State of autonomous vehicle safety regulation",
    "How small language models compare to frontier LLMs in 2026",
    "Progress in commercial fusion energy",
]

ICONS = {
    "search": '<svg viewBox="0 0 24 24" fill="none"><circle cx="10.5" cy="10.5" r="6.5" stroke="currentColor" stroke-width="1.8"/><line x1="15.3" y1="15.3" x2="21" y2="21" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
    "reader": '<svg viewBox="0 0 24 24" fill="none"><rect x="4.5" y="3" width="15" height="18" rx="1.5" stroke="currentColor" stroke-width="1.8"/><line x1="8" y1="8" x2="16" y2="8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><line x1="8" y1="12" x2="16" y2="12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><line x1="8" y1="16" x2="13" y2="16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    "writer": '<svg viewBox="0 0 24 24" fill="none"><path d="M4 20L4.7 16.6L15.6 5.7C16.2 5.1 17.1 5.1 17.7 5.7L18.8 6.8C19.4 7.4 19.4 8.3 18.8 8.9L7.9 19.8L4 20Z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><line x1="14" y1="7.3" x2="17.2" y2="10.5" stroke="currentColor" stroke-width="1.6"/></svg>',
    "critic": '<svg viewBox="0 0 24 24" fill="none"><path d="M12 3L19.5 6V11C19.5 15.5 16.5 19.3 12 21C7.5 19.3 4.5 15.5 4.5 11V6L12 3Z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="M9 11.5L11.2 13.7L15.2 9.3" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}

STATUS_LABEL = {"pending": "Pending", "active": "Running", "done": "Complete", "error": "Failed"}


# ====================================================================
# HELPERS
# ====================================================================
def now_str():
    return datetime.now().strftime("%H:%M:%S")


def fmt_secs(s):
    if s is None:
        return "--"
    return f"{s:.1f}s"


def render_pipeline_html(stage_state, overall_status_label):
    nodes_html = []
    for stage in STAGES:
        st_info = stage_state[stage["key"]]
        status = st_info["status"]
        elapsed = st_info["elapsed"]
        status_text = STATUS_LABEL[status] if status != "active" else stage["verb"] + "…"
        time_html = f'<div class="node-time">{fmt_secs(elapsed)}</div>' if status in ("done", "error") and elapsed else ""
        nodes_html.append(
            f'<div class="node {status}">'
            f'<div class="node-badge">{ICONS[stage["key"]]}</div>'
            f'<div class="node-num">{stage["sub"]}</div>'
            f'<div class="node-label">{stage["label"]}</div>'
            f'<div class="node-status">{status_text}</div>'
            f'{time_html}'
            f'</div>'
        )

    done_count = sum(1 for s in STAGES if stage_state[s["key"]]["status"] == "done")
    active_partial = 0.5 if any(stage_state[s["key"]]["status"] == "active" for s in STAGES) else 0.0
    progress_pct = min(100, int(((done_count + active_partial) / len(STAGES)) * 100))
    connector_fill = int((done_count / len(STAGES)) * 100)

    return (
        '<div class="pipeline-wrap">'
        '<div class="pipeline-head">'
        '<div class="pipeline-title">Multi-Agent Execution Pipeline</div>'
        f'<div class="pipeline-status-tag">{overall_status_label}</div>'
        '</div>'
        '<div style="position:relative;">'
        f'<div class="connector"><div class="connector-fill" style="width:{connector_fill}%;"></div></div>'
        f'<div class="node-row">{"".join(nodes_html)}</div>'
        '</div>'
        f'<div class="overall-bar-track"><div class="overall-bar-fill" style="width:{progress_pct}%;"></div></div>'
        '</div>'
    )


def render_log_html(log_events):
    lines = []
    for ev in log_events:
        cls = "ok" if ev["event"] == "done" else ("err" if ev["event"] == "error" else "")
        lines.append(f'<div class="log-line {cls}"><span class="log-time">{ev["time"]}</span>{html_lib.escape(ev["text"])}</div>')
    return '<div class="panel" style="margin-top:14px;"><div class="panel-title">Execution Log <span class="tag">LIVE</span></div>' + "".join(lines) + "</div>"


def extract_search_sources(search_text):
    if not search_text:
        return []
    sources = []
    pattern = re.compile(r"Title:\s*(.*?),\s*URL:\s*(\S+)")
    for m in pattern.finditer(search_text):
        title, url = m.group(1).strip(), m.group(2).strip()
        if url not in [s["url"] for s in sources]:
            sources.append({"title": title or url, "url": url})
    if not sources:
        for url in re.findall(r"https?://[^\s\)\]\"']+", search_text):
            if url not in [s["url"] for s in sources]:
                sources.append({"title": url, "url": url})
    return sources


def extract_report_urls(report_text):
    if not report_text:
        return []
    urls = re.findall(r"https?://[^\s\)\]\"'>,]+", report_text)
    seen, out = set(), []
    for u in urls:
        u = u.rstrip(").,")
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def parse_report_sections(report_text):
    if not report_text:
        return {}
    pattern = re.compile(
        r"(?im)^\s*#{0,3}\s*\**\s*[-\u2022]?\s*(Introduction|Key Findings|Conclusion|Sources|परिचय|मुख्य निष्कर्ष|निष्कर्ष|स्रोत|పరిచయం|ముఖ్య ఫలితాలు|ముగింపు|వనరులు|はじめに|主な知見|結論|情報源)\s*\**:?\s*$"
    )
    matches = list(pattern.finditer(report_text))
    if not matches:
        return {}
    sections = {}
    for i, m in enumerate(matches):
        name = m.group(1).strip().lower()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(report_text)
        sections[name] = report_text[start:end].strip()
    return sections


def extract_bullets(text):
    if not text:
        return []
    bullets = re.findall(r"(?m)^\s*[-\u2022*]\s*(.+)$", text)
    if bullets:
        return [b.strip() for b in bullets if b.strip()]
    numbered = re.findall(r"(?m)^\s*\d+[\.\)]\s*(.+)$", text)
    if numbered:
        return [b.strip() for b in numbered if b.strip()]
    parts = [p.strip() for p in text.split("\n") if p.strip()]
    return parts[:6]


def parse_critic_feedback(feedback_text):
    result = {"score": None, "strengths": [], "improvements": [], "verdict": ""}
    if not feedback_text:
        return result
    score_m = re.search(r"(?:\*\*)?Score:?(?:\*\*)?\s*(\d+(?:\.\d+)?)\s*/\s*10", feedback_text, re.I)
    if score_m:
        result["score"] = float(score_m.group(1))

    def grab(label_a, label_b):
        m = re.search(rf"(?:\*\*)?{label_a}(?:\*\*)?\s*:?\s*(.*?)(?=(?:\*\*)?{label_b}|$)", feedback_text, re.I | re.S)
        return m.group(1).strip() if m else ""

    strengths_txt = grab("Strengths", "Areas to Improve")
    improve_txt = grab("Areas to Improve", "One Line Verdict")
    verdict_m = re.search(r"(?:\*\*)?One Line Verdict(?:\*\*)?\s*:?\s*(.*)", feedback_text, re.I | re.S)

    result["strengths"] = extract_bullets(strengths_txt)
    result["improvements"] = extract_bullets(improve_txt)
    result["verdict"] = verdict_m.group(1).strip() if verdict_m else ""
    return result


def copy_button(text, key):
    payload = json.dumps(text)
    components.html(
        f"""
        <div style="font-family:'Inter',sans-serif;">
        <button id="copy-btn-{key}" style="
            background:#141D2C; color:#9BA8BE; border:1px solid #212C3D; border-radius:8px;
            padding:8px 16px; font-size:12.5px; cursor:pointer; font-family:'JetBrains Mono',monospace;
            letter-spacing:0.03em;">
            &#10697; Copy Report
        </button>
        <script>
        const btn = document.getElementById("copy-btn-{key}");
        btn.addEventListener("click", () => {{
            navigator.clipboard.writeText({payload});
            btn.innerText = "\u2713 Copied";
            btn.style.color = "#4FE8D3";
            btn.style.borderColor = "#4FE8D3";
            setTimeout(() => {{ btn.innerText = "\u29c9 Copy Report"; btn.style.color = "#9BA8BE"; btn.style.borderColor = "#212C3D"; }}, 1600);
        }});
        </script>
        </div>
        """,
        height=44,
    )


def build_download_bundle(topic, report_content, feedback_content):
    parts = [f"# Research Report: {topic}\n"]
    parts.append(f"_Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} — Language: {cur_lang}_\n\n---\n")
    parts.append(report_content)
    parts.append("\n\n---\n## Critic Review\n")
    parts.append(feedback_content)
    return "\n".join(parts)


# ====================================================================
# TOP NAVIGATION BAR (Language Translator & Theme Toggle)
# ====================================================================
nav_c1, nav_c2, nav_c3, nav_c4 = st.columns([4.2, 4.2, 2.2, 1.4])

with nav_c1:
    H(
        '<div style="display:flex; align-items:center; gap:8px; padding-top:6px;">'
        '<span style="font-family:var(--display); font-weight:700; font-size:16px; color:var(--text-hi);">Research Command Center</span>'
        '<span style="font-family:var(--mono); font-size:10px; color:var(--cyan); border:1px solid var(--cyan); border-radius:4px; padding:1px 6px;">4-AGENT</span>'
        '</div>'
    )

with nav_c2:
    lang_labels = [f"{LANGUAGES[l]['flag']} {l}" for l in LANGUAGE_LIST]
    cur_idx = LANGUAGE_LIST.index(cur_lang) if cur_lang in LANGUAGE_LIST else 0
    selected_pill = st.pills(
        "Language Navigation",
        options=lang_labels,
        default=lang_labels[cur_idx],
        label_visibility="collapsed",
        key="nav_lang_pills",
    )
    if selected_pill:
        for l in LANGUAGE_LIST:
            if l in selected_pill and l != st.session_state.selected_language:
                st.session_state.selected_language = l
                st.rerun()

with nav_c3:
    hist_count = len(st.session_state.history)
    hist_btn_label = f"💬 History ({hist_count})"
    if st.button(hist_btn_label, use_container_width=True, key="top_nav_hist_btn"):
        st.session_state.show_main_history = not st.session_state.get("show_main_history", False)
        st.rerun()

with nav_c4:
    toggle_icon = "☀️ Light" if st.session_state.theme == "dark" else "🌙 Dark"
    if st.button(toggle_icon, use_container_width=True, key="theme_toggle_btn"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

if st.session_state.get("show_main_history", False) and st.session_state.history:
    H(
        '<div style="background:var(--bg-panel); border:1px solid var(--border-bright); border-left:4px solid var(--cyan); border-radius:12px; padding:14px 18px; margin-bottom:16px;">'
        '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">'
        '<span style="font-family:var(--display); font-size:15px; font-weight:700; color:var(--text-hi);">📜 Saved Research History</span>'
        '<span style="font-family:var(--mono); font-size:11px; color:var(--cyan);">Click any chat to open into the main screen</span>'
        '</div>'
        '</div>'
    )
    cols = st.columns(min(len(st.session_state.history), 3))
    for i, h in enumerate(reversed(st.session_state.history)):
        c = cols[i % len(cols)]
        score_txt = f"⭐ {h['score']:g}/10" if h.get("score") is not None else ""
        short_t = (h.get("topic", "Untitled")[:28] + "…") if len(h.get("topic", "Untitled")) > 30 else h.get("topic", "Untitled")
        btn_txt = f"🔬 {short_t}\n🕒 {h.get('time', '')}  {score_txt}"
        is_cur = st.session_state.current and st.session_state.current.get("id") == h.get("id")
        if c.button(btn_txt, key=f"nav_drawer_h_{h.get('id', i)}_{i}", use_container_width=True, type="primary" if is_cur else "secondary"):
            st.session_state.current = h
            st.session_state.show_main_history = False
            st.session_state.form_nonce += 1
            st.rerun()


# ====================================================================
# SIDEBAR (Original structure preserved)
# ====================================================================
with st.sidebar:
    H(
        '<div class="brand-mark">'
        '<div class="brand-glyph">&#9670;</div>'
        '<div>'
        '<div class="brand-text-title">Research Command Center</div>'
        '<div class="brand-text-sub">Multi-Agent System</div>'
        '</div>'
        '</div>'
    )

    if st.button("✨  New Research  ➕", key="sidebar_new_chat_btn", use_container_width=True):
        st.session_state.current = None
        st.session_state.pending_query = None
        st.session_state.topic_input = ""
        st.session_state.form_nonce += 1
        st.rerun()

    H('<div class="side-section-label">System Status</div>')
    if IMPORT_ERROR:
        H('<div class="env-row"><span><span class="dot dot-bad"></span>Pipeline import</span><span>error</span></div>')
    else:
        H('<div class="env-row"><span><span class="dot dot-ok"></span>Pipeline</span><span>ready</span></div>')
    H('<div class="env-row"><span><span class="dot dot-ok"></span>Agents</span><span>4 online</span></div>')
    H(f'<div class="env-row"><span><span class="dot dot-ok"></span>Language</span><span>{cur_lang}</span></div>')

    H('<div class="side-section-label">Session Stats</div>')
    total_runs = len(st.session_state.history)
    scores = [h["score"] for h in st.session_state.history if h.get("score") is not None]
    avg_score = f"{sum(scores)/len(scores):.1f}" if scores else "--"
    H(
        f'<div class="stat-strip">'
        f'<div class="stat-box"><div class="stat-val">{total_runs}</div><div class="stat-lab">Reports</div></div>'
        f'<div class="stat-box"><div class="stat-val">{avg_score}</div><div class="stat-lab">Avg Score</div></div>'
        f'</div>'
    )

    H(f'<div class="side-section-label">Chat History ({total_runs})</div>')
    if not st.session_state.history:
        H('<div style="font-family:var(--mono); font-size:11.5px; color:var(--text-lo); padding:8px 0; text-align:center;">No past research chats yet.</div>')
    else:
        for i, h in enumerate(reversed(st.session_state.history)):
            real_idx = len(st.session_state.history) - 1 - i
            h_id = h.get("id", f"hist_{real_idx}")
            is_active = (
                st.session_state.current is not None
                and st.session_state.current.get("id") == h.get("id")
            )
            score_str = f"⭐ {h['score']:g}/10" if h.get("score") is not None else ""
            time_str = f"🕒 {h.get('time', '')}"
            meta_line = f"{time_str}   {score_str}".strip()
            topic_txt = h.get("topic", "Untitled")
            short_topic = (topic_txt[:26] + "…") if len(topic_txt) > 28 else topic_txt
            icon = "🟢" if is_active else "🔬"
            label = f"{icon}  {short_topic}\n{meta_line}"
            if st.button(
                label,
                key=f"hist_chat_{h_id}_{real_idx}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current = h
                st.session_state.pending_query = None
                st.session_state.topic_input = ""
                st.session_state.form_nonce += 1
                st.rerun()

        with st.expander("History Options"):
            if st.button("🗑️ Clear All Chats", key="clear_all_chats_btn", use_container_width=True):
                st.session_state.history = []
                st.session_state.current = None
                st.session_state.pending_query = None
                st.session_state.form_nonce += 1
                save_chat_history([])
                st.rerun()


# ====================================================================
# HERO + INPUT (Original structure preserved)
# ====================================================================
H('<div class="hero-eyebrow">Live Multi-Agent Research System</div>')
H('<div class="hero-title">Ask anything. Watch four agents<br><span>research it in real time.</span></div>')
H(
    '<div class="hero-sub">A search agent, a reader agent, a writer and a critic work in sequence &mdash; '
    'gathering sources, extracting content, drafting a structured report, and grading it. '
    'Every status update below reflects the pipeline\'s real execution.</div>'
)

# Voice Assistant Speech-to-Text Input Widget
render_voice_input_card(target_lang=cur_lang, theme=st.session_state.theme)

if st.session_state.history:
    with st.expander(f"📜 View Past Research History ({len(st.session_state.history)} saved sessions)", expanded=False):
        exp_cols = st.columns(min(len(st.session_state.history), 3))
        for i, h in enumerate(reversed(st.session_state.history)):
            c = exp_cols[i % len(exp_cols)]
            score_txt = f"⭐ {h['score']:g}/10" if h.get("score") is not None else ""
            short_t = (h.get("topic", "Untitled")[:28] + "…") if len(h.get("topic", "Untitled")) > 30 else h.get("topic", "Untitled")
            btn_txt = f"🔬 {short_t}\n🕒 {h.get('time', '')}  {score_txt}"
            is_cur = st.session_state.current and st.session_state.current.get("id") == h.get("id")
            if c.button(btn_txt, key=f"main_exp_h_{h.get('id', i)}_{i}", use_container_width=True, type="primary" if is_cur else "secondary"):
                st.session_state.current = h
                st.session_state.form_nonce += 1
                st.rerun()

H('<div class="chip-label">Quick-start queries</div>')
chip_cols = st.columns(len(EXAMPLE_QUERIES))
for i, ex in enumerate(EXAMPLE_QUERIES):
    if chip_cols[i].button(ex, key=f"chip_{i}", use_container_width=True):
        st.session_state.pending_query = ex
        st.session_state.auto_run = True
        st.rerun()

with st.form(key=f"research_form_{st.session_state.form_nonce}", clear_on_submit=True):
    topic = st.text_input(
        "Research Topic",
        value="",
        placeholder="e.g. Breakthroughs in solid-state EV batteries in 2026",
        key=f"topic_field_{st.session_state.form_nonce}",
    )
    c1, c2 = st.columns([2.2, 7.8])
    with c1:
        submitted = st.form_submit_button("Launch Research →", use_container_width=True)

# Determine query to run:
run_topic = None
if submitted and topic and topic.strip():
    run_topic = topic.strip()
elif st.session_state.auto_run and st.session_state.pending_query:
    run_topic = st.session_state.pending_query
    st.session_state.pending_query = None

st.session_state.auto_run = False
run_now = bool(run_topic)


# ====================================================================
# EXECUTE PIPELINE
# ====================================================================
if run_now:
    if IMPORT_ERROR:
        st.error(
            f"The research pipeline could not be imported, so no request was sent. "
            f"Fix this before running research:\n\n`{IMPORT_ERROR}`"
        )
    elif not run_topic or not run_topic.strip():
        st.warning("Enter a research topic before launching.")
    else:
        stage_state = {s["key"]: {"status": "pending", "elapsed": None, "start": None} for s in STAGES}
        log_events = []

        pipeline_placeholder = st.empty()
        log_placeholder = st.empty()

        overall_start = time.time()

        def redraw(overall_label):
            pipeline_placeholder.markdown(render_pipeline_html(stage_state, overall_label), unsafe_allow_html=True)
            log_placeholder.markdown(render_log_html(log_events), unsafe_allow_html=True)

        redraw("Initializing")

        def on_status(stage, event, data=None):
            info = next(s for s in STAGES if s["key"] == stage)
            if event == "start":
                stage_state[stage]["status"] = "active"
                stage_state[stage]["start"] = time.time()
                log_events.append({"time": now_str(), "event": "start", "text": f"{info['label']} agent started — {info['verb'].lower()}"})
                redraw(f"{info['label']} agent running")
            elif event == "done":
                started = stage_state[stage]["start"] or time.time()
                stage_state[stage]["status"] = "done"
                stage_state[stage]["elapsed"] = time.time() - started
                preview = (str(data)[:90] + "…") if data and len(str(data)) > 90 else str(data)
                log_events.append({"time": now_str(), "event": "done", "text": f"{info['label']} agent complete — {preview}"})
                redraw(f"{info['label']} complete")
            elif event == "error":
                started = stage_state[stage]["start"] or time.time()
                stage_state[stage]["status"] = "error"
                stage_state[stage]["elapsed"] = time.time() - started
                log_events.append({"time": now_str(), "event": "error", "text": f"{info['label']} agent failed — {data}"})
                redraw(f"{info['label']} failed")

        try:
            # If query is in Hindi, Telugu, or Japanese, translate to English for optimal web retrieval
            search_query = translate_query_to_english(run_topic.strip())

            with st.spinner(""):
                result = research_pipeline(search_query, status_callback=on_status)
            total_elapsed = time.time() - overall_start
            redraw(f"Complete in {fmt_secs(total_elapsed)}")

            critic_parsed = parse_critic_feedback(result.get("feedback", ""))
            history_entry = {
                "id": f"run_{int(time.time()*1000)}",
                "topic": run_topic.strip(),
                "time": datetime.now().strftime("%H:%M"),
                "result": result,
                "score": critic_parsed["score"],
                "duration": total_elapsed,
            }
            st.session_state.history.append(history_entry)
            st.session_state.current = history_entry
            save_chat_history(st.session_state.history)
            st.session_state.form_nonce += 1
            st.rerun()

        except Exception as e:  # noqa: BLE001
            H(
                f'<div class="panel" style="border-color:var(--rose);">'
                f'<div class="panel-title" style="color:var(--rose);">Pipeline Execution Failed</div>'
                f'<div style="font-family:var(--mono); font-size:12.5px; color:var(--text-mid); line-height:1.6;">'
                f'The agent that was running when this happened is marked <b style="color:var(--rose);">Failed</b> above. '
                f'Nothing below was fabricated to compensate &mdash; the run simply stopped here.<br><br>'
                f'<span style="color:var(--rose);">{html_lib.escape(str(e))}</span><br><br>'
                f'Common causes: missing/invalid <code>OPENROUTER_API_KEY</code> or <code>TAVILY_API_KEY</code> in <code>.env</code>, '
                f'no network access, or a rate limit from the model/search provider.'
                f'</div>'
                f'</div>'
            )
            st.session_state.current = None


# ====================================================================
# RENDER RESULTS (With Language Translation & Voice Playback)
# ====================================================================
entry = st.session_state.current
if entry:
    result = entry["result"]
    topic_display = entry["topic"]
    entry_id = entry.get("id", f"entry_{id(entry)}")

    raw_report = result.get("report", "") or ""
    raw_feedback = result.get("feedback", "") or ""
    search_results = result.get("search_results", "") or ""
    scraped = result.get("scraped_content", "") or ""

    # Dynamic translation if target language is Hindi, Telugu, or Japanese
    if cur_lang != "English":
        cache_key = f"{entry_id}_{cur_lang}"
        if cache_key not in st.session_state.translations:
            with st.spinner(f"Translating research report and analysis to {cur_lang} ({LANGUAGES[cur_lang]['native']})..."):
                translated_report = translate_text(raw_report, cur_lang, context="research report")
                translated_feedback = translate_text(raw_feedback, cur_lang, context="critic review")
                st.session_state.translations[cache_key] = {
                    "report": translated_report,
                    "feedback": translated_feedback,
                }
        cached = st.session_state.translations[cache_key]
        active_report = cached["report"]
        active_feedback = cached["feedback"]
    else:
        active_report = raw_report
        active_feedback = raw_feedback

    # Parse sections and findings from active report
    sections = parse_report_sections(active_report)
    findings_text = ""
    for k in ["key findings", "मुख्य निष्कर्ष", "ముఖ్య ఫలితాలు", "主な知見"]:
        if k in sections:
            findings_text = sections[k]
            break
    findings = extract_bullets(findings_text) if findings_text else []
    if not findings:
        findings = extract_bullets(active_report)[:4]

    critic = parse_critic_feedback(active_feedback)
    sources = extract_search_sources(search_results)
    report_urls = set(extract_report_urls(sections.get("sources", "") or active_report))

    score_display = f"{critic['score']:g}/10" if critic.get("score") is not None else "--"
    sources_count = len(sources) if sources else len(report_urls)
    findings_count = len(findings) if findings else "--"

    # ACTIVE CHAT SESSION BANNER
    ban_c1, ban_c2 = st.columns([8, 2])
    with ban_c1:
        H(
            f'<div style="background:var(--bg-panel); border:1px solid var(--border); border-left:4px solid var(--cyan); '
            f'border-radius:14px; padding:16px 20px; margin-top:20px; margin-bottom:12px;">'
            f'<div style="display:flex; align-items:center; gap:8px;">'
            f'<span style="font-family:var(--mono); font-size:10.5px; color:var(--cyan); letter-spacing:0.1em; text-transform:uppercase; font-weight:600;">ACTIVE RESEARCH SESSION</span>'
            f'<span style="font-family:var(--mono); font-size:10px; color:var(--text-lo); border:1px solid var(--border-bright); border-radius:4px; padding:1px 6px;">OPEN IN MAIN SCREEN</span>'
            f'</div>'
            f'<div style="font-family:var(--display); font-size:22px; font-weight:700; color:var(--text-hi); margin-top:4px; line-height:1.2;">'
            f'{html_lib.escape(topic_display)}'
            f'</div>'
            f'<div style="font-family:var(--mono); font-size:11px; color:var(--text-lo); margin-top:4px;">'
            f'Completed at {entry.get("time", "")} &bull; Total Runtime: {entry.get("duration", 0):.1f}s &bull; Critic Rating: {score_display}'
            f'</div>'
            f'</div>'
        )
    with ban_c2:
        H('<div style="height:20px;"></div>')
        if st.button("➕ New Research", key="banner_new_research_btn", use_container_width=True):
            st.session_state.current = None
            st.session_state.pending_query = None
            st.session_state.form_nonce += 1
            st.rerun()

    # Stat strip
    H(
        f'<div class="stat-strip" style="margin-top:4px;">'
        f'<div class="stat-box"><div class="stat-val">{entry["duration"]:.1f}s</div><div class="stat-lab">Total Runtime</div></div>'
        f'<div class="stat-box"><div class="stat-val">{sources_count}</div><div class="stat-lab">Sources Found</div></div>'
        f'<div class="stat-box"><div class="stat-val">{score_display}</div><div class="stat-lab">Critic Score</div></div>'
        f'<div class="stat-box"><div class="stat-val">{findings_count}</div><div class="stat-lab">Key Findings</div></div>'
        f'</div>'
    )

    # Voice Assistant Reader Bar (Listen to Report aloud in chosen language)
    summary_for_voice = (findings_text if findings_text else active_report[:800])
    render_voice_player_card(
        report_text=active_report,
        summary_text=summary_for_voice,
        target_lang=cur_lang,
        theme=st.session_state.theme,
        key=f"voice_{entry_id}_{cur_lang}"
    )

    tabs = st.tabs(["Report", "Key Findings", "Sources", "Critic Review", "Raw Agent Output"])

    # TAB 1: Report
    with tabs[0]:
        badge_lang = f"{LANGUAGES[cur_lang]['flag']} {cur_lang}"
        H(f'<div class="panel"><div class="panel-title">Final Report <span class="tag">{badge_lang}</span> <span class="tag">{html_lib.escape(topic_display)}</span></div></div>')
        st.markdown(active_report if active_report else "_No report was produced._")

        bcol1, bcol2 = st.columns([1, 1])
        with bcol1:
            copy_button(active_report, key=f"report_{entry_id}_{cur_lang}")
        with bcol2:
            st.download_button(
                "⬇ Download Full Report (.md)",
                data=build_download_bundle(topic_display, active_report, active_feedback),
                file_name=f"research_{cur_lang.lower()}_{re.sub(r'[^a-zA-Z0-9]+', '_', topic_display.lower())[:30]}.md",
                mime="text/markdown",
                use_container_width=True,
            )

    # TAB 2: Key Findings
    with tabs[1]:
        H('<div class="panel-title" style="margin-top:8px;">Key Findings</div>')
        if findings:
            for f in findings:
                H(f'<div class="finding-card">{html_lib.escape(f)}</div>')
        else:
            H('<div class="finding-card">No distinct "Key Findings" section was detected in the report\'s formatting &mdash; see the full report tab for content.</div>')

    # TAB 3: Sources
    with tabs[2]:
        H('<div class="panel-title" style="margin-top:8px;">Sources Discovered by the Search Agent</div>')
        if sources:
            for i, s in enumerate(sources, 1):
                H(
                    f'<div class="source-card">'
                    f'<div class="source-idx">SRC-{i:02d}</div>'
                    f'<div class="source-title">{html_lib.escape(s["title"])}</div>'
                    f'<div class="source-url"><a href="{html_lib.escape(s["url"])}" target="_blank">{html_lib.escape(s["url"])}</a></div>'
                    f'</div>'
                )
        elif report_urls:
            for i, u in enumerate(sorted(report_urls), 1):
                H(
                    f'<div class="source-card">'
                    f'<div class="source-idx">SRC-{i:02d}</div>'
                    f'<div class="source-url"><a href="{html_lib.escape(u)}" target="_blank">{html_lib.escape(u)}</a></div>'
                    f'</div>'
                )
        else:
            H('<div class="finding-card">No source URLs were detected in this run\'s output.</div>')

    # TAB 4: Critic Review
    with tabs[3]:
        H('<div class="panel-title" style="margin-top:8px;">Critic Agent Review</div>')
        if critic["score"] is not None:
            pct = critic["score"] / 10 * 100
            H(
                f'<div class="score-wrap">'
                f'<div><span class="score-num">{critic["score"]:g}</span><span class="score-of">/10</span></div>'
                f'<div class="score-track"><div class="score-fill" style="width:{pct}%;"></div></div>'
                f'</div>'
            )
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            H('<div style="font-family:var(--mono); font-size:11px; color:var(--green); letter-spacing:0.06em; text-transform:uppercase; margin-bottom:8px;">Strengths</div>')
            if critic["strengths"]:
                for s in critic["strengths"]:
                    H(f'<div class="finding-card" style="border-left-color:var(--green);">{html_lib.escape(s)}</div>')
            else:
                st.caption("Not detected in this run's output.")
        with fcol2:
            H('<div style="font-family:var(--mono); font-size:11px; color:var(--amber); letter-spacing:0.06em; text-transform:uppercase; margin-bottom:8px;">Areas to Improve</div>')
            if critic["improvements"]:
                for s in critic["improvements"]:
                    H(f'<div class="finding-card" style="border-left-color:var(--amber);">{html_lib.escape(s)}</div>')
            else:
                st.caption("Not detected in this run's output.")
        if critic["verdict"]:
            H(f'<div class="verdict-box">&ldquo;{html_lib.escape(critic["verdict"])}&rdquo;</div>')
        with st.expander("Full raw critic output"):
            st.code(active_feedback if isinstance(active_feedback, str) else str(active_feedback), language="markdown")

    # TAB 5: Raw Output
    with tabs[4]:
        H('<div class="panel-title" style="margin-top:8px;">Unprocessed Output Per Agent</div>')
        with st.expander("① Search Agent — raw output"):
            st.code(search_results, language="text")
        with st.expander("② Reader Agent — scraped content"):
            st.code(scraped, language="text")
        with st.expander("③ Writer Agent — generated report"):
            st.code(active_report, language="markdown")
        with st.expander("④ Critic Agent — review"):
            st.code(active_feedback, language="markdown")

elif not IMPORT_ERROR:
    H(
        '<div class="panel" style="text-align:center; padding:40px 24px;">'
        '<div style="font-family:var(--mono); font-size:12px; color:var(--text-lo); letter-spacing:0.08em; text-transform:uppercase;">Standing by</div>'
        '<div style="font-family:var(--display); font-size:16px; color:var(--text-mid); margin-top:8px;">'
        'Enter a topic above or click the microphone to speak, then launch research.'
        '</div>'
        '</div>'
    )
