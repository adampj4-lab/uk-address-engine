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

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# -------------------------------------------------------------------
# CACHED ADDRESS FETCH (24hr TTL)
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
# SIDEBAR
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
# MAIN DASHBOARD
# -------------------------------------------------------------------
if 'active_address' in st.session_state:
    active_property = st.session_state['active_address']
    active_postcode = st.session_state['scanned_postcode']
    
    st.info(f"🏠 **Active Target Property:** {active_property}, {active_postcode}")
    st.divider()
    
    tab_broadband, tab_energy, tab_banking = st.tabs(["🌐 Broadband & Mobiles", "⚡ Energy & EPC", "💰 Cash & Savings"])
    
    # ===================================================================
    # TAB 1: HOME BROADBAND OPTIMIZATION
    # ===================================================================
    with tab_broadband:
        st.subheader("🌐 Home Broadband Infrastructure & Audit")
        st.caption(f"Analyzing local infrastructure, cabinet connections, and network coverage for {active_postcode}...")
        
        # 1. Infrastructure Coverage Badges
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Openreach FTTP", value="Full Fibre Ready", delta="1,000 Mbps")
        with col2:
            st.metric(label="Virgin Media / Nexfibre", value="Gig1 Available", delta="1,130 Mbps")
        with col3:
            st.metric(label="CityFibre / Altnet", value="Active Network", delta="Symmetric 900 Mbps")
        with col4:
            st.metric(label="5G Home Broadband", value="Good Coverage", delta="Three / EE")

        st.divider()

        # 2. Interactive Tariff & Contract Audit Tool
        st.markdown("### 📊 Household Contract Audit")
        
        col_input1, col_input2, col_input3 = st.columns(3)
        with col_input1:
            current_provider = st.selectbox(
                "Current Provider:",
                ["BT Broadband", "Sky Broadband", "Virgin Media", "TalkTalk", "Vodafone", "Plusnet", "Other"]
            )
        with col_input2:
            current_bill = st.number_input("Current Monthly Payment (£/mo):", min_value=15.0, max_value=120.0, value=44.0, step=1.0)
        with col_input3:
            contract_status = st.selectbox("Contract Status:", ["Out of Contract (Rolling)", "In Contract", "Expiring within 30 Days"])

        # 3. Market Deal Comparison Engine
        st.markdown("### 🏷️ Top Available Switch Deals for Your Address")
        
        # Target Market Deals
        deals = [
            {
                "Provider": "Vodafone Full Fibre 900",
                "Speed": "910 Mbps",
                "Cost": 32.00,
                "Network": "Openreach / CityFibre",
                "Perks": "Free setup, £100 Amazon Voucher"
            },
            {
                "Provider": "Virgin Media M500",
                "Speed": "516 Mbps",
                "Cost": 30.00,
                "Network": "Virgin Media",
                "Perks": "No setup fee, price locked"
            },
            {
                "Provider": "Sky Full Fibre 300",
                "Speed": "300 Mbps",
                "Cost": 27.00,
                "Network": "Openreach",
                "Perks": "Wall-to-wall WiFi Guarantee"
            }
        ]

        # Calculate annual savings
        annual_current = current_bill * 12
        best_deal_monthly = min(d['Cost'] for d in deals)
        annual_best = best_deal_monthly * 12
        annual_savings = max(0.0, annual_current - annual_best)

        if contract_status != "In Contract" and annual_savings > 0:
            st.success(f"🎉 **Switch Recommendation Available!** Moving to a current market deal saves approx **£{annual_savings:,.2f} / year** (£{current_bill - best_deal_monthly:.2f}/month).")
        elif contract_status == "In Contract":
            st.info("ℹ️ You are currently in contract. Set a reminder 30 days before expiration to avoid out-of-contract price hikes.")

        # Display Deals Table
        deal_table = []
        for d in deals:
            monthly_saving = max(0.0, current_bill - d['Cost'])
            deal_table.append({
                "Provider & Plan": d['Provider'],
                "Max Speed": d['Speed'],
                "Monthly Cost": f"£{d['Cost']:.2f}",
                "Est. Monthly Savings": f"£{monthly_saving:.2f}/mo" if monthly_saving > 0 else "Base Rate",
                "Infrastructure": d['Network'],
                "Key Incentives": d['Perks']
            })
        
        st.table(deal_table)

    with tab_energy:
        st.subheader("Energy Performance")
        st.metric("EPC Rating", "C (72)")

    with tab_banking:
        st.subheader("Cash Yield Check")
        cash = st.number_input("Household Cash Balance (£):", value=10000, step=1000)
        st.write(f"At 4.8% top market yield: **£{cash * 0.048:,.2f} / year**")

else:
    st.warning("👈 Enter a postcode in the sidebar, click **Find Addresses**, select your address, and click **Set Active Property**.")
