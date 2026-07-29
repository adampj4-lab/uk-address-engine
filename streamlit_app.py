import streamlit as st
import requests
import urllib.parse
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Household Optimization Engine", page_icon="⚡", layout="wide")

st.title("⚡ Household Optimization Engine")
st.write("Scan your address to unlock savings on Broadband, Energy, and Household Bills.")

# Initialize Session States if they don't exist yet
if 'address_list' not in st.session_state:
    st.session_state['address_list'] = []
if 'scanned_postcode' not in st.session_state:
    st.session_state['scanned_postcode'] = ""

# -------------------------------------------------------------------
# CALLBACK FUNCTION: Fetches Addresses when "Find Addresses" is clicked
# -------------------------------------------------------------------
def fetch_addresses():
    raw_pc = st.session_state.postcode_input.strip().upper()
    if len(raw_pc) >= 5 and " " not in raw_pc:
        raw_pc = f"{raw_pc[:-3]} {raw_pc[-3:]}"
    
    st.session_state['scanned_postcode'] = raw_pc
    encoded_postcode = urllib.parse.quote(raw_pc)
    
    url = f"https://landregistry.data.gov.uk/data/ppi/transaction-record.json?propertyAddress.postcode={encoded_postcode}&_pageSize=200"
    
    try:
        res = requests.get(url, headers={'Accept': 'application/json'})
        if res.status_code == 200:
            items = res.json().get('result', {}).get('items', [])
            addresses = set()
            for item in items:
                paon = item.get('propertyAddress', {}).get('paon', '')
                saon = item.get('propertyAddress', {}).get('saon', '')
                street = item.get('propertyAddress', {}).get('street', '')
                full = f"{saon} {paon} {street}".strip()
                if full:
                    addresses.add(full)
            
            opts = sorted(list(addresses))
            opts.append("➕ Enter address manually...")
            st.session_state['address_list'] = opts
        else:
            st.error("Failed to fetch address list from API.")
    except Exception as e:
        st.error(f"Error connecting: {e}")

# -------------------------------------------------------------------
# STEP 1: Sidebar Location Setup
# -------------------------------------------------------------------
with st.sidebar:
    st.header("📍 Property Location")
    
    # Input widget with key
    st.text_input("Enter Postcode:", value="LS15 8JJ", key="postcode_input")
    
    # Button triggers callback directly
    st.button("Find Addresses", on_click=fetch_addresses)

    # Display dropdown IF address_list exists in state
    if st.session_state['address_list']:
        selected = st.selectbox("Select Your Address:", st.session_state['address_list'])
        
        final_address = selected
        if selected == "➕ Enter address manually...":
            custom = st.text_input("Type house number & street name:")
            final_address = custom.strip()
            
        if st.button("Set Active Property 🎯"):
            if final_address:
                st.session_state['active_address'] = final_address
                st.success("Target set!")
            else:
                st.warning("Please type an address.")

# -------------------------------------------------------------------
# STEP 2: Dashboard Content
# -------------------------------------------------------------------
if 'active_address' in st.session_state:
    active_property = st.session_state['active_address']
    active_postcode = st.session_state['scanned_postcode']
    
    st.info(f"🏠 **Active Target Property:** {active_property}, {active_postcode}")
    st.divider()
    
    tab_broadband, tab_energy, tab_banking = st.tabs(["🌐 Broadband & Mobiles", "⚡ Energy & EPC", "💰 Cash & Savings"])
    
    with tab_broadband:
        st.subheader("Broadband & Mobile Optimization")
        st.write(f"Checking connections for **{active_postcode}**...")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Estimated Max Speed", "900 Mbps", "Full Fibre (FTTP)")
        with col2:
            st.metric("Openreach / Altnet Status", "Connected")

    with tab_energy:
        st.subheader("Energy Performance")
        st.metric("EPC Benchmark Rating", "C (72)")

    with tab_banking:
        st.subheader("Lazy Cash Yield Check")
        cash = st.number_input("Household Cash Balance (£):", value=10000, step=1000)
        st.write(f"At 4.8% top market yield: **£{cash * 0.048:,.2f} / year** potential return.")

else:
    st.warning("👈 Enter a postcode in the sidebar, click **Find Addresses**, select your address, and click **Set Active Property**.")
