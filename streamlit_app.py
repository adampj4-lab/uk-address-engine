import streamlit as st
import requests
import re
import datetime

# Page Configuration
st.set_page_config(
    page_title="Household Optimization Engine", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
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
    .badge-speed {
        background-color: #f0fdf4;
        color: #166534;
    }
    .disclaimer-box {
        background-color: #fffbebfb;
        border: 1px solid #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #92400e;
        margin-bottom: 20px;
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
# MAIN DASHBOARD
# -------------------------------------------------------------------
st.title("⚡ Household Optimization Engine")
st.caption("Real-time property infrastructure scanning & cost optimization portal.")

if 'active_address' in st.session_state:
    active_property = st.session_state['active_address']
    active_postcode = st.session_state['scanned_postcode']
    
    st.info(f"🏠 **Active Property:** {active_property}, {active_postcode}")
    
    tab_broadband, tab_energy, tab_banking = st.tabs(["🌐 Broadband & Infrastructure", "⚡ Energy & EPC", "💰 Cash & Savings"])
    
    with tab_broadband:
        st.subheader("🌐 Network Infrastructure Availability")
        
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

        # -------------------------------------------------------------------
        # AUDIT FORM WITH OVERRIDE FUNCTIONALITY
        # -------------------------------------------------------------------
        st.markdown("### 📊 Household Contract & Speed Audit")
        
        col_in1, col_in2, col_in3 = st.columns(3)
        with col_in1:
            current_provider = st.selectbox(
                "Current Provider:",
                ["Vodafone", "BT Broadband", "Sky Broadband", "Virgin Media", "TalkTalk", "Plusnet", "EE", "Other"]
            )
        with col_in2:
            current_bill = st.number_input("Current Bill (£/mo):", min_value=10.0, max_value=150.0, value=30.0, step=1.0)
        with col_in3:
            current_speed = st.number_input("Current Speed (Mbps):", min_value=10, max_value=2000, value=65, step=25)

        col_in4, col_in5 = st.columns(2)
        with col_in4:
            contract_status = st.selectbox("Contract Status:", ["In Contract", "Out of Contract (Rolling)", "Expiring within 30 Days"])
        
        est_exit_fee = 0.0
        months_left = 0.0
        
        if contract_status == "In Contract":
            with col_in5:
                expiry_date = st.date_input(
                    "Contract Expiry Date (if known):", 
                    value=datetime.date(2027, 2, 5),
                    format="DD/MM/YYYY"
                )
            
            today = datetime.date.today()
            if expiry_date > today:
                days_left = (expiry_date - today).days
                months_left = round(days_left / 30.44, 1)
                
                # Formula: Bill x 0.80 x remaining months
                calc_fee = round((current_bill * 0.80) * months_left, 2)
                
                # Checkbox allowing exact quote entry
                override_fee = st.checkbox("I know my exact provider exit fee quote")
                
                if override_fee:
                    est_exit_fee = st.number_input("Enter Exact Exit Fee (£):", min_value=0.0, value=65.00, step=5.0)
                else:
                    est_exit_fee = calc_fee
                    st.caption(f"⏱️ **Contract Expiry:** {expiry_date.strftime('%d/%m/%Y')} (~{months_left} months remaining). Indicative exit fee: **~£{est_exit_fee:.2f}**")
        else:
            with col_in5:
                st.write("")

        # Deals Database
        deals = [
            {
                "Provider": "EE Full Fibre 900",
                "Speed_Mbps": 900,
                "Speed_Display": "900 Mbps",
                "Cost": 25.99,
                "Network": "Openreach FTTP",
                "Switch_Credit": 100.00,
                "Perks": "£100 Switch Credit / Contract Buyout"
            },
            {
                "Provider": "Vodafone Full Fibre 900",
                "Speed_Mbps": 910,
                "Speed_Display": "910 Mbps",
                "Cost": 32.00,
                "Network": "Openreach / CityFibre",
                "Switch_Credit": 100.00,
                "Perks": "Up to £100 Switch Credit / Gift Card"
            },
            {
                "Provider": "Virgin Media Gig1",
                "Speed_Mbps": 1130,
                "Speed_Display": "1,130 Mbps",
                "Cost": 39.00,
                "Network": "Virgin Cable / Nexfibre",
                "Switch_Credit": 100.00,
                "Perks": "£100 Bill Credit towards contract buyout"
            }
        ]

        st.markdown("---")
        st.markdown("### 🏷️ Market Options vs Your Current Package")
        
        # PROMINENT DISCLAIMER BOX
        st.markdown("""
        <div class="disclaimer-box">
            ⚠️ <strong>Disclaimer on Early Termination Fees:</strong> Contract exit costs and switch credit absorbency shown below are <strong>estimates for guidance only</strong> based on standard UK industry calculations (less VAT & non-consumed service charges). Always verify your exact early exit fee directly with your current provider before placing a switch order.
        </div>
        """, unsafe_allow_html=True)

        for d in deals:
            # 1. Price Differential
            monthly_diff = current_bill - d['Cost']
            annual_net_saving = monthly_diff * 12

            # 2. Speed Differential
            speed_diff = d['Speed_Mbps'] - current_speed
            speed_text = f"🚀 +{speed_diff} Mbps Faster" if speed_diff > 0 else f"📉 {abs(speed_diff)} Mbps Slower"

            # 3. Buyout Credit Math against Exit Fee
            net_switch_cost = max(0.0, est_exit_fee - d['Switch_Credit'])
            
            buyout_html = ""
            if contract_status == "In Contract" and est_exit_fee > 0:
                if d['Switch_Credit'] >= est_exit_fee:
                    buyout_html = f"<div style='font-size: 0.85rem; color: #16a34a; font-weight: 600; margin-top: 6px;'>✅ Switch Credit (£{d['Switch_Credit']:.0f}) covers your £{est_exit_fee:.2f} exit fee!</div>"
                else:
                    buyout_html = f"<div style='font-size: 0.85rem; color: #d97706; font-weight: 600; margin-top: 6px;'>⚡ Credit covers £{d['Switch_Credit']:.0f} of exit fee (Net cost to leave now: £{net_switch_cost:.2f})</div>"

            # Financial Verdict Formatting
            if monthly_diff > 0:
                financial_text = f"Save £{monthly_diff:.2f}/mo (£{annual_net_saving:.2f}/yr)"
                financial_color = "#16a34a"
            elif monthly_diff < 0:
                financial_text = f"+£{abs(monthly_diff):.2f}/mo for speed upgrade"
                financial_color = "#d97706"
            else:
                financial_text = "Same Monthly Cost"
                financial_color = "#475569"

            st.markdown(f"""
            <div class="deal-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="deal-title">{d['Provider']}</div>
                        <div style="margin-top: 6px;">
                            <span class="badge badge-speed">{d['Speed_Display']} ({speed_text})</span>
                            <span class="badge">🌐 {d['Network']}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">🎁 {d['Perks']}</div>
                        {buyout_html}
                    </div>
                    <div style="text-align: right;">
                        <div class="deal-price">£{d['Cost']:.2f} <span style="font-size: 0.8rem; font-weight: normal; color: #64748b;">/mo</span></div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: {financial_color};">{financial_text}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab_energy:
        st.subheader("⚡ Energy & EPC Performance")
        st.metric("Current EPC Rating", "C (72)", "Potential: B (85)")

    with tab_banking:
        st.subheader("💰 Cash & Savings Optimization")
        cash = st.number_input("Household Cash Balance (£):", value=10000, step=1000)
        st.metric("Target Market Yield (4.8%)", f"£{cash * 0.048:,.2f} / year")

else:
    st.warning("👈 Enter a postcode in the sidebar, search addresses, and click **Confirm Active Property** to unlock your audit.")
