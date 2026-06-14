"""
Data Engine Modul.
Zuständig für API Requests an wspr.live, Caching-Mechanismen und Datei-Management.
"""
import io
import os
import glob
import time
import hashlib
import threading
import uuid
from datetime import datetime
from pathlib import Path
import requests
import pandas as pd
import streamlit as st

from config import DB_URL, CACHE_DIR, CACHE_TTL_SEC
from core.snr_utils import round_snr_like_columns

# HTTP Session für Wiederverwendung von Verbindungen
http_session = requests.Session()
http_session.headers.update({'Accept-Encoding': 'gzip, deflate'})
_query_file_locks = {}
_query_file_locks_guard = threading.Lock()


def _query_lock(cache_key):
    with _query_file_locks_guard:
        return _query_file_locks.setdefault(cache_key, threading.Lock())


def _set_data_source(source, db_hit=False):
    st.session_state._db_hit = bool(db_hit)
    st.session_state._data_source = source


def _query_cache_path(sql_query):
    digest = hashlib.sha256(sql_query.encode("utf-8")).hexdigest()
    return Path(CACHE_DIR) / f"query_{digest}.parquet"

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
    _set_data_source("wspr.live", db_hit=True)
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

        df = round_snr_like_columns(df)
            
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


def _read_query_parquet(path):
    df = pd.read_parquet(path)
    int_cols = [
        "time_slot",
        "target_seen",
        "external_seen",
        "opportunity",
        "hit",
        "miss",
        "target_only",
    ]
    for column in int_cols:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], downcast="integer")
    return round_snr_like_columns(df)


def _fetch_wspr_parquet(sql_query, is_demo=False):
    """
    Stream a compact Parquet result to an exact-query disk cache.

    This path intentionally avoids ``st.cache_data`` so a monthly Absolute
    evidence table is not retained as a shared deserialized DataFrame in RAM.
    """
    cache_path = _query_cache_path(sql_query)
    lock = _query_lock(cache_path.stem)

    with lock:
        if cache_path.exists():
            age = time.time() - cache_path.stat().st_mtime
            if is_demo or age <= CACHE_TTL_SEC:
                _set_data_source("disk cache", db_hit=False)
                try:
                    return _read_query_parquet(cache_path)
                except (OSError, ValueError):
                    try:
                        cache_path.unlink()
                    except OSError:
                        pass

        start_time = time.time()
        _set_data_source("wspr.live", db_hit=True)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] EXECUTING PARQUET QUERY:\n{sql_query}\n")
        temp_path = cache_path.with_name(f"{cache_path.stem}.{uuid.uuid4().hex}.tmp")

        try:
            with http_session.get(
                DB_URL,
                params={"query": sql_query},
                stream=True,
                timeout=(10, 180),
            ) as resp:
                if resp.status_code != 200:
                    st.error(f"CLICKHOUSE DATABASE ERROR {resp.status_code}")
                    st.code(resp.text, language="text")
                    st.warning("The failed SQL query was:")
                    st.code(sql_query, language="sql")
                    return None

                with temp_path.open("wb") as handle:
                    for chunk in resp.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            handle.write(chunk)

            if not temp_path.exists() or temp_path.stat().st_size == 0:
                return None

            temp_path.replace(cache_path)
            df = _read_query_parquet(cache_path)
            elapsed = time.time() - start_time
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] CACHE MISS: "
                f"DB Parquet Query Executed in {elapsed:.2f}s | "
                f"Payload: {cache_path.stat().st_size / 1024:.1f} KB"
            )
            return df if not df.empty else None
        except (requests.RequestException, OSError, ValueError) as exc:
            st.error(f"WSPR data request failed: {exc}")
            return None
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

@st.cache_data(ttl=None, show_spinner=False)
def _fetch_wspr_data_demo(sql_query):
    """Holt WSPR-Daten für die Demo (ohne TTL / unendliches Caching)."""
    _set_data_source("wspr.live", db_hit=True)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] EXECUTING DEMO QUERY:\n{sql_query}\n")
    
    resp = http_session.get(DB_URL, params={'query': sql_query})
    
    if resp.status_code == 200 and len(resp.text.strip().split('\n')) > 1:
        return round_snr_like_columns(pd.read_csv(io.StringIO(resp.text), engine='pyarrow'))
    elif resp.status_code != 200:
        # 2. BEI EINEM FEHLER: Schreie laut auf der UI!
        st.error(f"🛑 **CLICKHOUSE DEMO-FEHLER {resp.status_code}**")
        st.code(resp.text, language="text")
        st.warning("Die fehlgeschlagene SQL-Abfrage war:")
        st.code(sql_query, language="sql")
        
    return None

def fetch_wspr_data(sql_query, is_demo=False, response_format="csv"):
    """Hauptfunktion zum Abrufen von WSPR-Daten, routet basierend auf Demo-Modus."""
    if str(response_format).lower() == "parquet":
        return _fetch_wspr_parquet(sql_query, is_demo=is_demo)
    if is_demo: return _fetch_wspr_data_demo(sql_query)
    return _fetch_wspr_data_standard(sql_query)
