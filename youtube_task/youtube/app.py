import streamlit as st
from about.app import app as about_page
from video_downloader.app import app as video_downloader
from transcript_downloader.app import app as transcript_downloader
from thumbnail_downloader.app import app as thumbnail_downloader
from channel_downloader.app import app as channel_downloader
from persistence import load_persistent_state, save_persistent_state, clear_persistent_state
import re, datetime

# Set page configuration with the new app name.
st.set_page_config(page_title="Youtube Task", layout="wide")

# --- Load persistent state from disk ---
if "persistent_state" not in st.session_state:
    st.session_state["persistent_state"] = load_persistent_state()
persistent_state = st.session_state["persistent_state"]

# On startup, if a cookie string is saved in persistent state, load it into session state.
if "youtube_cookies" in persistent_state:
    st.session_state.youtube_cookies = persistent_state["youtube_cookies"]
else:
    st.session_state.youtube_cookies = ""

# Branding header in the sidebar.
st.sidebar.markdown("""
    <div style="text-align: center;">
        <h1 style="color: #FF0000;">🎬 Youtube Task</h1>
        <p style="font-size: 14px;">All your YouTube utilities in one place</p>
    </div>
    <hr>
""", unsafe_allow_html=True)

# Sidebar navigation options with icons.
page = st.sidebar.radio(
    "Navigation",
    options=["About", "Channel Downloader", "Video Downloader", "Transcript Downloader", "Thumbnail Downloader"],
    index=0,
    format_func=lambda x: {
        "About": "💡 About",
        "Channel Downloader": "📕 Channel Downloader",
        "Video Downloader": "🎞️ Video Downloader",
        "Transcript Downloader": "📜 Transcript Downloader",
        "Thumbnail Downloader": "📌 Thumbnail Downloader"
    }[x]
)

# --- YouTube Cookies Input at the Bottom of the Sidebar ---
st.sidebar.markdown("---")
st.sidebar.markdown("### YouTube Cookies")

# Read cookie input (defaulting to what is stored persistently).
cookies_input = st.sidebar.text_area(
    label="Paste your YouTube cookies here",
    value=st.session_state.get("youtube_cookies", ""),
    height=100,
    key="youtube_cookies_input",
)
# Save the cookie string into session state.
st.session_state.youtube_cookies = cookies_input

def parse_cookies_expiry_range(cookies: str):
    """
    Parses a Netscape cookie file string to determine the expiry range.
    Returns a tuple (earliest_date, latest_date) where both are datetime objects.
    If no expiry is found, returns (None, None).
    """
    lines = cookies.splitlines()
    expiries = []
    for line in lines:
        line = line.strip()
        # Skip comments and empty lines.
        if not line or line.startswith("#"):
            continue
        # Netscape cookie file: domain, flag, path, secure, expiry, name, value
        parts = re.split(r"\s+", line)
        if len(parts) < 7:
            continue
        try:
            expiry_ts = int(parts[4])
            expiries.append(expiry_ts)
        except Exception:
            continue
    if expiries:
        earliest_ts = min(expiries)
        latest_ts = max(expiries)
        earliest_date = datetime.datetime.fromtimestamp(earliest_ts)
        latest_date = datetime.datetime.fromtimestamp(latest_ts)
        return earliest_date, latest_date
    return None, None

if cookies_input:
    earliest, latest = parse_cookies_expiry_range(cookies_input)
    now = datetime.datetime.now()
    if earliest and latest:
        if latest < now:
            st.sidebar.error(f"Cookies expired. Range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}")
        else:
            st.sidebar.info(f"Cookies valid until {latest.strftime('%Y-%m-%d')} (earliest expiry: {earliest.strftime('%Y-%m-%d')})")
            # Save the valid cookies into persistent state.
            persistent_state["youtube_cookies"] = cookies_input
            persistent_state["youtube_cookies_latest_expiry"] = latest.strftime("%Y-%m-%d")
            save_persistent_state(persistent_state)
            st.session_state["persistent_state"] = persistent_state
    else:
        st.sidebar.warning("Could not parse expiry date from cookies. Ensure your cookies include expiry information in Netscape format.")

# --- Button to Clear Persistent State (including cookies) ---
if st.sidebar.button("Clear Persistent State Including Files"):
    new_state = clear_persistent_state()
    st.session_state["persistent_state"] = new_state
    st.session_state.youtube_cookies = ""
    st.experimental_rerun()
# Main content area navigation.
if page == "About":
    about_page()
elif page == "Channel Downloader":
    channel_downloader()
elif page == "Video Downloader":
    video_downloader()
elif page == "Transcript Downloader":
    transcript_downloader()
elif page == "Thumbnail Downloader":
    thumbnail_downloader()
