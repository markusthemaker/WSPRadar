"""
Data Engine Modul.
Zuständig für API Requests an wspr.live, Caching-Mechanismen und Datei-Management.
"""
import io
import os
import glob
import time
from datetime import datetime
import requests
import pandas as pd
import streamlit as st

from config import DB_URL, CACHE_DIR, CACHE_TTL_SEC

# HTTP Session für Wiederverwendung von Verbindungen
http_session = requests.Session()
http_session.headers.update({'Accept-Encoding': 'gzip, deflate'})

def cleanup_old_parquets():
    """Löscht Cache-Dateien, die älter als CACHE_TTL_SEC sind, robust gegen Race-Conditions."""
    now = time.time()
    for f in glob.glob(f"{CACHE_DIR}/*.parquet"):
        try:
            if os.stat(f).st_mtime < now - CACHE_TTL_SEC:
                os.remove(f)
        except OSError:
            pass

# Führe Cleanup beim Import aus (analog zur alten monolithischen app.py)
cleanup_old_parquets()

@st.cache_data(ttl=CACHE_TTL_SEC, show_spinner=False)
def _fetch_wspr_data_standard(sql_query):
    """Holt WSPR-Daten regulär mit Caching (TTL)."""
    st.session_state._db_hit = True 
    start_time = time.time()
    
    # 1. Logge die Query heimlich in die Konsole
    print(f"[{datetime.now().strftime('%H:%M:%S')}] EXECUTING QUERY:\n{sql_query}\n")
    
    resp = http_session.get(DB_URL, params={'query': sql_query})    
    if resp.status_code == 200 and len(resp.text.strip().split('\n')) > 1:
        df = pd.read_csv(io.StringIO(resp.text), engine='pyarrow')
        float_cols = ['snr', 'power', 'stat_val', 'snr_u_norm', 'snr_r_norm', 'peer_lat', 'peer_lon', 'best_ref_dist']
        for c in float_cols:
            if c in df.columns: df[c] = pd.to_numeric(df[c], downcast='float')
            
        int_cols = ['has_u', 'has_r', 'is_me', 'time_slot']
        for c in int_cols:
            if c in df.columns: df[c] = pd.to_numeric(df[c], downcast='integer')
            
        elapsed = time.time() - start_time
        print(f"[{datetime.now().strftime('%H:%M:%S')}] CACHE MISS: DB Query Executed in {elapsed:.2f}s | Payload: {len(resp.content)/1024:.1f} KB")
        return df
    elif resp.status_code != 200:
        # 2. BEI EINEM FEHLER: Schreie laut auf der UI!
        st.error(f"🛑 **CLICKHOUSE DATENBANK-FEHLER {resp.status_code}**")
        st.code(resp.text, language="text")
        st.warning("Die fehlgeschlagene SQL-Abfrage war:")
        st.code(sql_query, language="sql")
        
    return None

@st.cache_data(ttl=None, show_spinner=False)
def _fetch_wspr_data_demo(sql_query):
    """Holt WSPR-Daten für die Demo (ohne TTL / unendliches Caching)."""
    st.session_state._db_hit = True
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] EXECUTING DEMO QUERY:\n{sql_query}\n")
    
    resp = http_session.get(DB_URL, params={'query': sql_query})
    
    if resp.status_code == 200 and len(resp.text.strip().split('\n')) > 1:
        return pd.read_csv(io.StringIO(resp.text), engine='pyarrow')
    elif resp.status_code != 200:
        # 2. BEI EINEM FEHLER: Schreie laut auf der UI!
        st.error(f"🛑 **CLICKHOUSE DEMO-FEHLER {resp.status_code}**")
        st.code(resp.text, language="text")
        st.warning("Die fehlgeschlagene SQL-Abfrage war:")
        st.code(sql_query, language="sql")
        
    return None

def fetch_wspr_data(sql_query, is_demo=False):
    """Hauptfunktion zum Abrufen von WSPR-Daten, routet basierend auf Demo-Modus."""
    if is_demo: return _fetch_wspr_data_demo(sql_query)
    return _fetch_wspr_data_standard(sql_query)