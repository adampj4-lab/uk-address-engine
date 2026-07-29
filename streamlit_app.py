import streamlit as st
import requests
import re

# Page Configuration
st.set_page_config(
    page_title="Household Optimization Engine", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling cards, badges, and layout
st.markdown("""
<style>
    /* Global Container Styling */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Card Container */
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
    
    /* Custom Provider Card */
    .deal-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #2563eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 15px;
    }
    
    .deal-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .deal-price {
        font-size: 1.4rem;
        font-weight: 800;
        color: #16a34a;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #e0f2fe;
        color: #0369a1;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

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
    st.title("📍 Property Search")
    st.caption("Select a postcode and lock in your active address context.")
    
    st.text_input("Postcode:", value="LS15 8JJ", key="postcode_input")
    st.button("🔍 Find Addresses", on_click=fetch_addresses, use_container_width=True)

    if st.session_state['address_list']:
        st.divider()
        selected = st.selectbox("Select Your Address:", st.session_state['address_list'])
        if st.button("🎯 Confirm Active Property", use_container_width=True, type="primary"):
            st.session_state['active_address'] = selected
            st.success("Target set!")

# -------------------------------------------------------------------
# MAIN HEADER & DASHBOARD
# -------------------------------------------------------------------
st.title("⚡ Household Optimization Engine")
st.caption("Real-time property infrastructure scanning & cost optimization portal.")

if 'active_address' in st.session_state:
    active_property = st.session_state['active_address']
    active_postcode = st.session_state['scanned_postcode']
    
    # Active Context Banner
    st.info(f"🏠 **Active Property:** {active_property}, {active_postcode}")
    
    tab_broadband, tab_energy, tab_banking = st.tabs(["🌐 Broadband & Infrastructure", "⚡ Energy & EPC", "💰 Cash & Savings"])
    
    # ===================================================================
    # TAB 1: HOME BROADBAND OPTIMIZATION (STYLIZED)
    # ===================================================================
    with tab_broadband:
        st.subheader("🌐 Network Infrastructure Availability")
        
        # 1. Styled Infrastructure Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Openreach FTTP", value="Ready", delta="1,000 Mbps")
        with col2:
            st.metric(label="Virgin Media / Nexfibre", value="Gig1", delta="1,130 Mbps")
        with col3:
            st.metric(label="CityFibre Altnet", value="Active", delta="900 Mbps Sym")
        with col4:
            st.metric(label="5G Home Broadband", value="Excellent", delta="EE / Three")

        st.divider()

        # 2. Audit Form Container
        st.markdown("### 📊 Household Contract Audit")
        
        with st.container():
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

        # Target Deals
        deals = [
            {
                "Provider": "Vodafone Full Fibre 900",
                "Speed": "910 Mbps",
                "Cost": 32.00,
                "Network": "Openreach / CityFibre",
                "Perks": "Free setup, £100 Amazon Gift Card"
            },
            {
                "Provider": "Virgin Media M500",
                "Speed": "516 Mbps",
                "Cost": 30.00,
                "Network": "Virgin Media Cable",
                "Perks": "No setup fee, price locked for 18 mo"
            },
            {
                "Provider": "Sky Full Fibre 300",
                "Speed": "300 Mbps",
                "Cost": 27.00,
                "Network": "Openreach FTTP",
                "Perks": "Wall-to-wall WiFi Guarantee"
            }
        ]

        # Calculate savings
        best_deal_monthly = min(d['Cost'] for d in deals)
        annual_savings = max(0.0, (current_bill - best_deal_monthly) * 12)

        st.markdown("---")
        
        if contract_status != "In Contract" and annual_savings > 0:
            st.success(f"🎉 **Switch Recommendation Available:** Moving to a top-tier market deal saves **£{annual_savings:,.2f} / year** (£{current_bill - best_deal_monthly:.2f}/month).")
        elif contract_status == "In Contract":
            st.info("ℹ️ You are currently in contract. Set a reminder 30 days before expiration to lock in a new rate.")

        st.markdown("### 🏷️ Top Available Switch Deals")
        
        # 3. Individual Styled Card UI for Deals
        for d in deals:
            monthly_saving = max(0.0, current_bill - d['Cost'])
            saving_text = f"Save £{monthly_saving:.2f}/mo" if monthly_saving > 0 else "Base Rate"
            
            st.markdown(f"""
            <div class="deal-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="deal-title">{d['Provider']}</div>
                        <div style="margin-top: 5px;">
                            <span class="badge">⚡ {d['Speed']}</span>
                            <span class="badge">🌐 {d['Network']}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">🎁 {d['Perks']}</div>
                    </div>
                    <div style="text-align: right;">
                        <div class="deal-price">£{d['Cost']:.2f} <span style="font-size: 0.8rem; font-weight: normal; color: #64748b;">/mo</span></div>
                        <div style="font-size: 0.85rem; font-weight: 600; color: #16a34a;">{saving_text}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ===================================================================
    # TAB 2 & 3 PLACEHOLDERS
    # ===================================================================
    with tab_energy:
        st.subheader("⚡ Energy & EPC Performance")
        st.metric("Current EPC Rating", "C (72)", "Potential: B (85)")

    with tab_banking:
        st.subheader("💰 Cash & Savings Optimization")
        cash = st.number_input("Household Cash Balance (£):", value=10000, step=1000)
        st.metric("Target Market Yield (4.8%)", f"£{cash * 0.048:,.2f} / year")

else:
    st.warning("👈 Enter a postcode in the sidebar, search addresses, and click **Confirm Active Property** to unlock your audit.")
