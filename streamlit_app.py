import streamlit as st
import requests
import re

# Page Configuration
st.set_page_config(page_title="Household Optimization Engine", page_icon="⚡", layout="wide")

st.title("⚡ Household Optimization Engine")
st.write("Scan your address to unlock savings on Broadband, Energy, and Household Bills.")

# -------------------------------------------------------------------
# CONFIG & STATE INITIALIZATION
# -------------------------------------------------------------------
IDEAL_POSTCODES_API_KEY = "ak_test"

if 'address_list' not in st.session_state:
    st.session_state['address_list'] = []
if 'scanned_postcode' not in st.session_state:
    st.session_state['scanned_postcode'] = ""

# Helper function for natural sorting (e.g. 1, 2, 10 instead of 1, 10, 2)
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# -------------------------------------------------------------------
# CACHED API CALL (24hr TTL)
# -------------------------------------------------------------------
@st.cache_data(ttl=86400)
def get_cached_addresses(clean_postcode):
    url = f"https://api.ideal-postcodes.co.uk/v1/postcodes/{clean_postcode}?api_key={IDEAL_POSTCODES_API_KEY}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            items = data.get('result', [])
            addresses = []
            for item in items:
                line_1 = item.get('line_1', '')
                line_2 = item.get('line_2', '')
                post_town = item.get('post_town', '')
                full_addr = f"{line_1}, {line_2}, {post_town}".replace(", ,", ",").strip(", ")
                if full_addr:
                    addresses.append(full_addr)
            return sorted(addresses, key=natural_sort_key)
        else:
            return []
    except Exception:
        return []

# -------------------------------------------------------------------
# CALLBACK FUNCTION
# -------------------------------------------------------------------
def fetch_addresses():
    raw_pc = st.session_state.postcode_input.strip().upper()
    if len(raw_pc) >= 5 and " " not in raw_pc:
        raw_pc = f"{raw_pc[:-3]} {raw_pc[-3:]}"
    
    st.session_state['scanned_postcode'] = raw_pc
    clean_pc = raw_pc.replace(" ", "")
    
    address_list = get_cached_addresses(clean_pc)
    
    if address_list:
        st.session_state['address_list'] = address_list
    else:
        st.session_state['address_list'] = []
        st.error("No addresses found or API limit reached. Try 'ID1 1ED' for testing.")

# -------------------------------------------------------------------
# STEP 1: SIDEBAR NAVIGATION
# -------------------------------------------------------------------
with st.sidebar:
    st.header("📍 Property Location")
    
    st.text_input("Enter Postcode:", value="LS15 8JJ", key="postcode_input")
    st.button("Find Addresses", on_click=fetch_addresses)

    if st.session_state['address_list']:
        selected = st.selectbox("Select Your Address:", st.session_state['address_list'])
        
        if st.button("Set Active Property 🎯"):
            st.session_state['active_address'] = selected
            st.success("Target set!")

# -------------------------------------------------------------------
# STEP 2: DASHBOARD
# -------------------------------------------------------------------
if 'active_address' in st.session_state:
    active_property = st.session_state['active_address']
    active_postcode = st.session_state['scanned_postcode']
    
    st.info(f"🏠 **Active Target Property:** {active_property}, {active_postcode}")
    st.divider()
    
    tab_broadband, tab_energy, tab_banking = st.tabs(["🌐 Broadband & Mobiles", "⚡ Energy & EPC", "💰 Cash & Savings"])
    
    with tab_broadband:
        st.subheader("Broadband Availability")
        st.write(f"Checking infrastructure for **{active_property}**...")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Max Fibre Speed", "900 Mbps", "FTTP")
        with col2:
            st.metric("Openreach / Altnet", "Available")

    with tab_energy:
        st.subheader("Energy Performance")
        st.metric("EPC Rating", "C (72)")

    with tab_banking:
        st.subheader("Cash Yield Check")
        cash = st.number_input("Household Cash Balance (£):", value=10000, step=1000)
        st.write(f"At 4.8% top market yield: **£{cash * 0.048:,.2f} / year**")

else:
    st.warning("👈 Enter a postcode in the sidebar, click **Find Addresses**, select your address, and click **Set Active Property**.")
