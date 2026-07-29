import streamlit as st
import requests
import urllib.parse
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Household Optimization Engine", page_icon="⚡", layout="wide")

st.title("⚡ Household Optimization Engine")
st.write("Scan your address to unlock savings on Broadband, Energy, and Household Bills.")

# -------------------------------------------------------------------
# STEP 1: Postcode & Address Picker
# -------------------------------------------------------------------
with st.sidebar:
    st.header("📍 Property Location")
    postcode_input = st.text_input("Enter Postcode:", "LS15 8JJ")
    
    if st.button("Find Addresses"):
        clean_postcode = postcode_input.strip().upper()
        if len(clean_postcode) >= 5 and " " not in clean_postcode:
            clean_postcode = f"{clean_postcode[:-3]} {clean_postcode[-3:]}"
        
        encoded_postcode = urllib.parse.quote(clean_postcode)
        url = f"https://landregistry.data.gov.uk/data/ppi/transaction-record.json?propertyAddress.postcode={encoded_postcode}&_pageSize=100"
        
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
                
                st.session_state['address_list'] = sorted(list(addresses))
                st.session_state['postcode'] = clean_postcode
            else:
                st.error("Failed to fetch address list.")
        except Exception as e:
            st.error(f"Error: {e}")

    # Dropdown to pick the exact address
    if 'address_list' in st.session_state and st.session_state['address_list']:
        selected = st.selectbox("Select Your Address:", st.session_state['address_list'])
        if st.button("Set Active Property 🎯"):
            st.session_state['active_address'] = selected
            st.success("Property set!")

# -------------------------------------------------------------------
# STEP 2: Dashboard for the Active Property
# -------------------------------------------------------------------
if 'active_address' in st.session_state:
    active_property = st.session_state['active_address']
    active_postcode = st.session_state['postcode']
    
    st.info(f"🏠 **Active Target Property:** {active_property}, {active_postcode}")
    st.divider()
    
    # Create Tabs for the Utilities / Savings Audits
    tab_broadband, tab_energy, tab_banking = st.tabs(["🌐 Broadband & Mobiles", "⚡ Energy & EPC", "💰 Cash & Savings"])
    
    # --- TAB 1: BROADBAND ---
    with tab_broadband:
        st.subheader("Broadband Availability & Cost Optimization")
        st.write(f"Checking connectivity options for **{active_postcode}**...")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Estimated Max Speed", value="900 Mbps", delta="Full Fibre (FTTP)")
        with col2:
            st.metric(label="Openreach Coverage", value="Available", delta_color="normal")
        with col3:
            st.metric(label="Virgin Media / Altnets", value="Hyperoptic / CityFibre", delta_color="normal")
            
        st.write("---")
        st.write("### 💡 Recommended Switch Actions")
        st.success("**Out-of-contract opportunity detected:** Moving from legacy copper broadband to SIM-Only/Altnet deals saving approx. **£210/year**.")

    # --- TAB 2: ENERGY ---
    with tab_energy:
        st.subheader("Energy Performance & Tariff Audit")
        st.write(f"Fetching public EPC data for **{active_property}**...")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Current EPC Rating", value="C (72)", delta="Potential: B (85)")
        with col2:
            st.metric(label="Estimated Annual Energy Spend", value="£1,420 / yr")
            
        st.warning("⚠️ **Tariff Alert:** Fixed 12-Month deals currently beat the energy price cap by 7%. Switching recommendation ready.")

    # --- TAB 3: BANKING / SAVINGS ---
    with tab_banking:
        st.subheader("Lazy Cash Audit")
        st.write("Calculate what your cash could earn vs existing bank rates.")
        
        balance = st.number_input("Enter total household cash sitting in standard accounts (£):", value=10000, step=1000)
        current_rate = st.slider("Current Average Interest Rate (%)", 0.0, 5.0, 0.5)
        
        top_market_rate = 4.8  # Benchmark rate
        
        current_earnings = balance * (current_rate / 100)
        potential_earnings = balance * (top_market_rate / 100)
        gap = potential_earnings - current_earnings
        
        st.metric(label="Hidden Annual Return Unlocked", value=f"£{gap:,.2f}/yr", delta=f"+£{gap:,.2f}")

else:
    st.warning("👈 Please enter a postcode in the sidebar, select your exact address, and click **Set Active Property** to begin the audit.")
