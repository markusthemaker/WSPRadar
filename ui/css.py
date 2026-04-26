"""
CSS & Theming Module.
Contains all global custom CSS overrides to style the Streamlit frontend.
Separating this keeps the main orchestrator (app.py) free from markup clutter.
"""

import streamlit as st

def apply_custom_css():
    """
    Injects the custom CSS definitions into the Streamlit DOM.
    Handles fonts, button styling, dropdown state overrides, and mobile responsiveness.
    """
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');
        html, body, [class*="css"] { font-family: 'Space Mono', monospace !important; }
        .stApp { background-color: #050a15; background-image: radial-gradient(circle at 50% 50%, #0a1428 0%, #02040a 100%); color: #e0e0e0; }
        
        .block-container { max-width: 1024px !important; padding-top: 2rem !important; }
        
        /* Primary Run Buttons */
        div.stButton > button[kind="primary"] {
            background-color: transparent !important; color: #39ff14 !important; border: 2px solid #39ff14 !important;
            font-family: 'Space Mono', monospace !important; font-size: 1.0rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 1px; box-shadow: 0 0 10px rgba(57, 255, 20, 0.2), inset 0 0 10px rgba(57, 255, 20, 0.1); transition: all 0.3s ease;
        }
        div.stButton > button[kind="primary"]:hover { background-color: rgba(57, 255, 20, 0.1) !important; box-shadow: 0 0 20px rgba(57, 255, 20, 0.6), inset 0 0 15px rgba(57, 255, 20, 0.3); }
        
        /* Secondary Buttons (Reset, Demo) */
        div.stButton > button[kind="secondary"] { border-color: rgba(57, 255, 20, 0.5) !important; color: #e0e0e0 !important; font-size: 0.85rem !important; padding: 0.2rem 0.5rem !important; margin-top: 10px; transition: all 0.3s ease; }
        div.stButton > button[kind="secondary"]:hover { border-color: #39ff14 !important; color: #39ff14 !important; box-shadow: 0 0 10px rgba(57, 255, 20, 0.2) !important; }
        div.stButton > button[kind="tertiary"], div.stDownloadButton > button[kind="tertiary"] { text-decoration: none !important; }
        div.stButton > button[kind="tertiary"] *, div.stDownloadButton > button[kind="tertiary"] * { text-decoration: none !important; }

        /* Selectbox (Language Selector) aligned with button styling */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background-color: transparent !important;
            border: 1px solid rgba(57, 255, 20, 0.5) !important;
            border-radius: 0.5rem !important;
            color: #e0e0e0 !important;
            font-family: 'Space Mono', monospace !important;
            min-height: 40px !important; 
            margin-top: 10px; 
            transition: all 0.3s ease;
            cursor: pointer;
        }
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
            border-color: #39ff14 !important;
            box-shadow: 0 0 10px rgba(57, 255, 20, 0.2) !important;
        }
        
        /* Force absolute centering of the inner text container in selectboxes */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div > div:first-child {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            padding-left: 24px; /* Visual compensation for the right-side arrow icon */
        }

        /* Enforce font and size inside the closed select field */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
            font-family: 'Space Mono', monospace !important;
            font-size: 0.85rem !important;
            color: inherit !important;
            text-align: center !important;
        }
                
        /* Colorize the dropdown arrow icon */
        div[data-testid="stSelectbox"] svg {
            fill: #39ff14 !important;
        }
        
        /* Disabled State via :has() Pseudo-Class */
        div[data-testid="stSelectbox"]:has(input[disabled]) div[data-baseweb="select"] > div {
            border-color: rgba(255, 255, 255, 0.2) !important;
            background-color: transparent !important;
            cursor: not-allowed !important;
        }
        div[data-testid="stSelectbox"]:has(input[disabled]) div[data-baseweb="select"] > div:hover {
            border-color: rgba(255, 255, 255, 0.2) !important;
            box-shadow: none !important;
        }
        div[data-testid="stSelectbox"]:has(input[disabled]) svg {
            fill: #888888 !important;
        }
        
        /* Style the opened dropdown menu (Popover) */
        div[data-baseweb="popover"] ul {
            background-color: #0a1428 !important;
            border: 1px solid #39ff14 !important;
            border-radius: 0.5rem !important;
        }
        div[data-baseweb="popover"] ul li {
            font-family: 'Space Mono', monospace !important;
            font-size: 0.85rem !important;
            color: #e0e0e0 !important;
            background-color: transparent !important;
            text-align: center !important;
        }
        div[data-baseweb="popover"] ul li:hover {
            color: #39ff14 !important;
            background-color: rgba(57, 255, 20, 0.1) !important;
        }

        /* Expander and Text elements */
        label[data-testid="stWidgetLabel"] p, label[data-testid="stWidgetLabel"] div, div[data-testid="stRadio"] p, label[data-testid="stCheckbox"] p, label[data-testid="stCheckbox"] span { font-family: 'Space Mono', monospace !important; font-size: 14px !important; font-weight: 700 !important; color: #cccccc !important; }
        summary[data-testid="stExpanderToggle"] p { font-family: 'Space Mono', monospace !important; font-size: 16px !important; font-weight: 700 !important; color: #39ff14 !important; text-transform: uppercase; letter-spacing: 1px; }
        h3.section-title { font-family: 'Rajdhani', sans-serif !important; font-size: 2rem !important; color: #ffffff !important; border-bottom: 1px solid rgba(57, 255, 20, 0.3); padding-bottom: 10px; margin-top: 1.5rem; margin-bottom: 1.5rem; letter-spacing: 1px; }
        
        /* Markdown rendering inside the documentation */
        .stMarkdown h3 { color: #39ff14 !important; border-bottom: 1px solid rgba(57, 255, 20, 0.3); padding-bottom: 8px; margin-top: 2.5rem; font-family: 'Rajdhani', sans-serif !important; font-size: 1.8rem; letter-spacing: 1px; }
        .stMarkdown h4 { color: #ffffff !important; margin-top: 1.8rem; font-size: 1.2rem; font-weight: 700; text-transform: uppercase; }
        .stMarkdown p:has(> strong:only-child) {
            font-size: 1.05rem;
            line-height: 1.35;
            margin-top: 1.2rem;
            margin-bottom: 0.35rem;
        }
        .stMarkdown p:has(> strong:only-child) strong {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        .stMarkdown ol, .stMarkdown ul { padding-left: 2.5rem !important; margin-top: 0.5rem; }
        .stMarkdown ul { list-style-type: disc !important; list-style-position: outside !important; }
        .stMarkdown ol { list-style-type: decimal !important; list-style-position: outside !important; }
        .stMarkdown li { margin-bottom: 0.8rem; }
        .stMarkdown li::marker { color: #39ff14 !important; }
        .stMarkdown a { color: #39ff14 !important; text-decoration: underline !important; text-underline-offset: 3px; }
        .stMarkdown a:hover { color: #a6ff8a !important; }

        .stMarkdown,
        .stMarkdown p,
        .stMarkdown li {
            max-width: 100% !important;
            overflow-wrap: anywhere !important;
            word-break: break-word !important;
        }
        
        .stMarkdown a {
            color: #39ff14 !important;
            text-decoration: underline !important;
            text-underline-offset: 3px;
            overflow-wrap: anywhere !important;
            word-break: break-word !important;
        }
        
        .stMarkdown code {
            white-space: pre-wrap !important;
            overflow-wrap: anywhere !important;
            word-break: break-word !important;
        }
        
        .stMarkdown pre {
            max-width: 100% !important;
            white-space: pre-wrap !important;
            overflow-x: hidden !important;
        }

        a.header-anchor { display: none !important; }
        
        /* Visibility helpers */
        .pc-break { display: inline; }
        .mobile-pipe { display: none; }
        
        /* Mobile Responsiveness tweaks */
        @media (max-width: 768px) {
            .block-container { padding-top: 1.5rem !important; } 
            
            /* Mobile List Indentation Fix: Less padding saves horizontal space */
            .stMarkdown ol, .stMarkdown ul { padding-left: 1.1rem !important; }
            .stMarkdown li { margin-bottom: 0.5rem; font-size: 0.9rem; }
            
            /* Fix massive vertical gaps when columns with gap="large" stack on mobile */
            div[data-testid="stHorizontalBlock"] { gap: 0.5rem !important; }
                
            .header-container { 
                flex-wrap: wrap !important; 
                padding-bottom: 0.3rem !important; 
                margin-bottom: 0.5rem !important; 
                justify-content: center !important;
                align-items: center !important;
            }
            .text-container { display: contents !important; }
            img.main-logo { display: block !important; width: 65px !important; height: 65px !important; margin-right: 12px !important; margin-bottom: 0 !important; }
            h1.main-title { font-size: 2.8rem !important; text-align: left !important; line-height: 1.0 !important; margin: 0 !important; }
            h2.main-subtitle { 
                width: 100% !important; 
                font-size: 0.83rem !important; 
                letter-spacing: 0.5px !important; 
                margin-top: 2px !important; 
                text-align: center !important; 
                margin-left: 0px !important; 
                white-space: normal !important; 
                line-height: 1.3 !important; 
            }
            
            .dev-credit-container { font-size: 0.7rem !important; line-height: 1.3 !important; padding: 0 5px !important; margin-bottom: 1rem !important; }
            .pc-break { display: none !important; }
            .mobile-pipe { display: inline !important; }
        }
    </style>
    """, unsafe_allow_html=True)
