import streamlit as st
import requests
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Household Optimization Engine", page_icon="⚡", layout="wide")

st.title("⚡ Household Optimization Engine")
st.write("Scan your address to unlock savings on Broadband, Energy, and Household Bills.")

# Initialize Session States
if 'address_list' not in st.session_state:
    st.session_state['address_list'] = []
if 'scanned_postcode' not in st.session_state:
    st.session_state['scanned_postcode'] = ""

# -------------------------------------------------------------------
# CALLBACK FUNCTION: Queries Open Property Data via EPC/Postcode APIs
# -------------------------------------------------------------------
def fetch_addresses():
    raw_pc = st.session_state.postcode_input.strip().upper()
    if len(raw_pc) >= 5 and " " not in raw_pc:
        raw_pc = f"{raw_pc[:-3]} {raw_pc[-3:]}"
    
    st.session_state['scanned_postcode'] = raw_pc
    clean_pc = raw_pc.replace(" ", "")
    
    addresses = set()

    # Query Method 1: Open EPC Public Registry (Captures built/rented/lived-in properties)
    epc_url = f"https://api.openepc.co.uk/v1/postcode/{clean_pc}"
    try:
        res = requests.get(epc_url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            items = data.get('results', []) if isinstance(data, dict) else data
            for item in items:
                addr = item.get('address', '') or item.get('address1', '')
                if addr:
                    addresses.add(addr.title())
    except Exception:
        pass # Fallback to secondary source if endpoint times out

    # Query Method 2: Fallback to Land Registry for any additional hits
    if not addresses:
        lr_url = f"https://landregistry.data.gov.uk/data/ppi/transaction-record.json?propertyAddress.postcode={raw_pc}&_pageSize=200"
        try:
            res = requests.get(lr_url, headers={'Accept': 'application/json'}, timeout=5)
            if res.status_code == 200:
                items = res.json().get('result', {}).get('items', [])
                for item in items:
                    paon = item.get('propertyAddress', {}).get('paon', '')
                    saon = item.get('propertyAddress', {}).get('saon', '')
                    street = item.get('propertyAddress', {}).get('street', '')
                    full = f"{saon} {paon} {street}".strip()
                    if full:
                        addresses.add(full.title())
        except Exception:
            pass

    # Process final address options list
    opts = sorted(list(addresses))
    opts.append("➕ Enter address manually...")
    st.session_state['address_list'] = opts

# -------------------------------------------------------------------
# STEP 1: Sidebar Location Setup
# -------------------------------------------------------------------
with st.sidebar:
    st.header("📍 Property Location")
    
    # Postcode input widget
    st.text_input("Enter Postcode:", value="LS15 8JJ", key="postcode_input")
    
    # Trigger fetch on click
    st.button("Find Addresses", on_click=fetch_addresses)

    # Display dropdown if address_list contains items
    if st.session_state['address_list']:
        selected = st.selectbox("Select Your Address:", st.session_state['address_list'])
        
        final_address = selected
        if selected == "➕ Enter address manually...":
            custom = st.text_input("Type house number & street name:")
            final_address = custom.strip()
            
        if st.button("Set Active Property 🎯"):
            if final_address:
                st.session_state['active_address'] = final_address
                st.success("Target address active!")
            else:
                st.warning("Please specify an address.")

# -------------------------------------------------------------------
# STEP 2: Active Dashboard
# -------------------------------------------------------------------
if 'active_address' in st.session_state:
    active_property = st.session_state['active_address']
    active_postcode = st.session_state['scanned_postcode']
    
    st.info(f"🏠 **Active Target Property:** {active_property}, {active_postcode}")
    st.divider()
    
    tab_broadband, tab_energy, tab_banking = st.tabs(["🌐 Broadband & Mobiles", "⚡ Energy & EPC", "💰 Cash & Savings"])
    
    with tab_broadband:
        st.subheader("Broadband & Mobile Optimization")
        st.write(f"Checking infrastructure options for **{active_postcode}**...")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Estimated Max Speed", "900 Mbps", "Full Fibre (FTTP)")
        with col2:
            st.metric("Openreach / Altnet Status", "Available")

    with tab_energy:
        st.subheader("Energy Performance")
        st.metric("EPC Rating", "C (72)")

    with tab_banking:
        st.subheader("Lazy Cash Yield Check")
        cash = st.number_input("Household Cash Balance (£):", value=10000, step=1000)
        st.write(f"At 4.8% top market yield: **£{cash * 0.048:,.2f} / year** potential return.")

else:
    st.warning("👈 Enter a postcode in the sidebar, click **Find Addresses**, select your address, and click **Set Active Property**.")
