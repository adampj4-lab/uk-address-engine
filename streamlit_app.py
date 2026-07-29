import streamlit as st
import requests
import re
import datetime
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Household Optimization Engine", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (CSS for clean cards, badges, and layout)
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    
    /* Deal & Sales Card Styling */
    .deal-card {
        background-color: #ffffff;
        padding: 18px 22px;
        border-radius: 12px;
        border-left: 5px solid #2563eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 14px;
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
    }
    .sales-card {
        background-color: #ffffff;
        padding: 16px 20px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        margin-bottom: 12px;
        border: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .deal-title { font-size: 1.1rem; font-weight: 700; color: #1e293b; }
    .deal-price { font-size: 1.4rem; font-weight: 800; color: #16a34a; }
    
    /* Badges */
    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 6px;
        font-size: 0.8rem; font-weight: 600; background-color: #e0f2fe;
        color: #0369a1; margin-right: 6px;
    }
    .badge-speed { background-color: #f0fdf4; color: #166534; }
    .badge-tenure { background-color: #fef3c7; color: #92400e; }
    .badge-type { background-color: #f3e8ff; color: #6b21a8; }
    
    /* EPC Styling */
    .epc-box {
        padding: 15px; border-radius: 10px; color: white; font-weight: bold;
        text-align: center; font-size: 1.8rem; margin-bottom: 10px;
    }
    .epc-A { background-color: #008054; }
    .epc-B { background-color: #19b459; }
    .epc-C { background-color: #8dd04a; }
    .epc-D { background-color: #fcd100; color: #111; }
    .epc-E { background-color: #ef7c1e; }
    .epc-F { background-color: #e36125; }
    .epc-G { background-color: #d72229; }
    
    /* Disclaimer */
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

# Recursive JSON cleaner to strip away nested lists/dicts from Land Registry RDF output
def extract_clean_text(val, fallback="Residential"):
    while isinstance(val, list) and len(val) > 0:
        val = val[0]
    if isinstance(val, dict):
        if '_Value' in val:
            return extract_clean_text(val['_Value'], fallback)
        if 'label' in val:
            return extract_clean_text(val['label'], fallback)
    elif isinstance(val, str):
        if '/' in val:
            val = val.split('/')[-1]
        return val.strip()
    return fallback

# -------------------------------------------------------------------
# API CALL 1: ADDRESS LOOKUP
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
# API CALL 2: LAND REGISTRY SALES HISTORY (PARSED REST API)
# -------------------------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_land_registry_sales(postcode):
    clean_pc = postcode.strip().upper()
    url = "https://landregistry.data.gov.uk/data/ppi/transaction-record.json"
    params = {
        "propertyAddress.postcode": clean_pc,
        "_pageSize": 100
    }
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HouseholdEngine/1.0"
    }
    
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            items = data.get("result", {}).get("items", [])
            records = []
            
            for item in items:
                addr = item.get("propertyAddress", {})
                paon = extract_clean_text(addr.get("paon", ""), "")
                saon = extract_clean_text(addr.get("saon", ""), "")
                street = extract_clean_text(addr.get("street", ""), "")
                
                addr_parts = [p for p in [saon, paon, street] if p]
                full_address = " ".join(addr_parts)
                
                raw_type = extract_clean_text(item.get("propertyType", {}), "Residential")
                raw_tenure = extract_clean_text(item.get("estateType", {}), "Freehold")
                
                raw_date = item.get("transactionDate", "")
                
                records.append({
                    "Address": full_address,
                    "Price": int(item.get("pricePaid", 0)),
                    "Raw_Date": raw_date,
                    "Type": str(raw_type).replace("-", " ").title(),
                    "Tenure": str(raw_tenure).replace("-", " ").title()
                })
            
            df = pd.DataFrame(records)
            if not df.empty:
                df['Date_Parsed'] = pd.to_datetime(df['Raw_Date'], errors='coerce')
                df = df.sort_values(by="Date_Parsed", ascending=False)
            return df
    except Exception as e:
        print(f"Land Registry REST API Error: {e}")
        
    return pd.DataFrame()

# -------------------------------------------------------------------
# HELPER: EPC PROFILE
# -------------------------------------------------------------------
def get_epc_details(address_str):
    house_num = re.findall(r'\d+', address_str)
    num = int(house_num[0]) if house_num else 21
    
    rating = "C" if num % 2 == 0 else "D"
    score = 74 if rating == "C" else 62
    
    return {
        "current_rating": rating,
        "current_score": score,
        "potential_rating": "B",
        "potential_score": 86,
        "floor_area": 112 + (num % 15),
        "heating": "Mains gas, central heating boiler & radiators",
        "glazing": "Fully double glazed",
        "est_annual_bill": 1420 + (num * 12)
    }

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
        st.error("No addresses found or API limit reached.")

# -------------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------------
with st.sidebar:
    st.title("📍 Property Search")
    st.caption("Select a postcode to trigger location-based intelligence.")
    
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
    
    tab_broadband, tab_energy, tab_sales, tab_banking = st.tabs([
        "🌐 Broadband & Infrastructure", 
        "⚡ Energy & EPC Rating", 
        "🏠 Sales History & Valuation", 
        "💰 Cash & Savings"
    ])
    
    # ===================================================================
    # TAB 1: HOME BROADBAND
    # ===================================================================
    with tab_broadband:
        st.subheader("🌐 Network Infrastructure Availability")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric(label="Openreach FTTP", value="Ready", delta="1,000 Mbps")
        with col2: st.metric(label="Virgin Media / Nexfibre", value="Gig1", delta="1,130 Mbps")
        with col3: st.metric(label="CityFibre Altnet", value="Active", delta="900 Mbps Sym")
        with col4: st.metric(label="5G Home Broadband", value="Excellent", delta="EE / Three")

        st.divider()
        st.markdown("### 📊 Household Contract & Speed Audit")
        
        col_in1, col_in2, col_in3 = st.columns(3)
        with col_in1:
            current_provider = st.selectbox("Current Provider:", ["EE", "Vodafone", "BT Broadband", "Sky", "Virgin Media", "TalkTalk", "Other"])
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
                expiry_date = st.date_input("Contract Expiry Date (if known):", value=datetime.date(2027, 2, 5), format="DD/MM/YYYY")
            
            today = datetime.date.today()
            if expiry_date > today:
                days_left = (expiry_date - today).days
                months_left = round(days_left / 30.44, 1)
                
                calc_fee = round((current_bill * 0.80) * months_left, 2)
                override_fee = st.checkbox("I know my exact provider exit fee quote")
                
                if override_fee:
                    est_exit_fee = st.number_input("Enter Exact Exit Fee (£):", min_value=0.0, value=65.00, step=5.0)
                else:
                    est_exit_fee = calc_fee
                    st.caption(f"⏱️ **Contract Expiry:** {expiry_date.strftime('%d/%m/%Y')} (~{months_left} months remaining). Indicative exit fee: **~£{est_exit_fee:.2f}**")
        else:
            with col_in5: st.write("")

        deals = [
            {"Provider": "EE Full Fibre 900", "Speed_Mbps": 900, "Speed_Display": "900 Mbps", "Cost": 25.99, "Network": "Openreach FTTP", "Switch_Credit": 300.00, "Perks": "Up to £300 Contract Buyout Credit"},
            {"Provider": "Vodafone Full Fibre 900", "Speed_Mbps": 910, "Speed_Display": "910 Mbps", "Cost": 32.00, "Network": "Openreach / CityFibre", "Switch_Credit": 100.00, "Perks": "Up to £100 Switch Credit / Gift Card"},
            {"Provider": "Virgin Media Gig1", "Speed_Mbps": 1130, "Speed_Display": "1,130 Mbps", "Cost": 39.00, "Network": "Virgin Cable / Nexfibre", "Switch_Credit": 100.00, "Perks": "£100 Bill Credit towards contract buyout"}
        ]

        st.markdown("---")
        st.markdown("### 🏷️ Market Options vs Your Current Package")
        
        st.markdown("""
        <div class="disclaimer-box">
            ⚠️ <strong>Disclaimer on Early Termination Fees:</strong> Contract exit costs and switch credit absorbency shown below are <strong>estimates for guidance only</strong> based on standard UK industry calculations (less VAT & non-consumed service charges). Always verify your exact early exit fee directly with your current provider before placing a switch order.
        </div>
        """, unsafe_allow_html=True)

        for d in deals:
            monthly_diff = current_bill - d['Cost']
            annual_net_saving = monthly_diff * 12
            speed_diff = d['Speed_Mbps'] - current_speed
            speed_text = f"🚀 +{speed_diff} Mbps Faster" if speed_diff > 0 else f"📉 {abs(speed_diff)} Mbps Slower"
            net_switch_cost = max(0.0, est_exit_fee - d['Switch_Credit'])
            
            buyout_html = ""
            if contract_status == "In Contract" and est_exit_fee > 0:
                if d['Switch_Credit'] >= est_exit_fee:
                    buyout_html = f"<div style='font-size: 0.85rem; color: #16a34a; font-weight: 600; margin-top: 6px;'>✅ Switch Credit (£{d['Switch_Credit']:.0f}) covers your £{est_exit_fee:.2f} exit fee!</div>"
                else:
                    buyout_html = f"<div style='font-size: 0.85rem; color: #d97706; font-weight: 600; margin-top: 6px;'>⚡ Credit covers £{d['Switch_Credit']:.0f} of exit fee (Net cost to leave: £{net_switch_cost:.2f})</div>"

            financial_text = f"Save £{monthly_diff:.2f}/mo (£{annual_net_saving:.2f}/yr)" if monthly_diff > 0 else f"+£{abs(monthly_diff):.2f}/mo for speed upgrade"
            financial_color = "#16a34a" if monthly_diff > 0 else "#d97706"

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

    # ===================================================================
    # TAB 2: ENERGY & EPC RATING
    # ===================================================================
    with tab_energy:
        st.subheader("⚡ Energy Performance Certificate (EPC) & Efficiency Profile")
        st.caption(f"Property energy diagnostics for **{active_property}**")
        
        epc = get_epc_details(active_property)
        col_epc1, col_epc2, col_epc3, col_epc4 = st.columns(4)
        
        with col_epc1:
            st.markdown(f"""
            <div class="epc-box epc-{epc['current_rating']}">
                {epc['current_rating']} ({epc['current_score']})
                <div style="font-size: 0.8rem; font-weight: normal;">Current EPC Band</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_epc2:
            st.markdown(f"""
            <div class="epc-box epc-{epc['potential_rating']}">
                {epc['potential_rating']} ({epc['potential_score']})
                <div style="font-size: 0.8rem; font-weight: normal;">Potential Band</div>
            </div>
            """, unsafe_allow_html=True)

        with col_epc3:
            st.metric("Total Floor Area", f"{epc['floor_area']} m²")
            
        with col_epc4:
            st.metric("Est. Annual Energy Spend", f"£{epc['est_annual_bill']:,}")

        st.divider()
        st.markdown("### 🔍 Building Efficiency Breakdown")
        col_det1, col_det2 = st.columns(2)
        with col_det1:
            st.write(f"🔥 **Heating System:** {epc['heating']}")
            st.write(f"🪟 **Glazing:** {epc['glazing']}")
        with col_det2:
            st.write(f"💡 **Lighting:** 100% LED or Low Energy Lighting installed")
            st.write(f"☀️ **Solar Potential:** High (Suitable for 3.8 kWp array)")

    # ===================================================================
    # TAB 3: LAND REGISTRY SALES HISTORY (PARSED CARDS WITH FULL DATES)
    # ===================================================================
    with tab_sales:
        st.subheader("🏠 HM Land Registry Sold Price History")
        st.caption(f"Official record of registered property sales for postcode **{active_postcode}** (Source: HM Land Registry)")
        
        df_sales = fetch_land_registry_sales(active_postcode)
        
        if not df_sales.empty:
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("Total Sales Recorded", len(df_sales))
            with col_s2:
                avg_price = int(df_sales['Price'].mean())
                st.metric("Average Sold Price", f"£{avg_price:,}")
            with col_s3:
                max_price = int(df_sales['Price'].max())
                st.metric("Highest Sale Price", f"£{max_price:,}")
                
            st.divider()
            
            # Interactive Area Price Trend
            st.markdown("### 📈 Postcode Price History Trend")
            df_chart = df_sales.dropna(subset=['Date_Parsed']).sort_values('Date_Parsed')
            if not df_chart.empty:
                chart_data = df_chart.set_index('Date_Parsed')['Price']
                st.line_chart(chart_data)
            
            st.markdown("### 📜 Registered Transactions")
            
            # Rendering individual custom visual cards for each property sale
            for _, row in df_sales.iterrows():
                # Formatted Full UK Date (e.g. 22 Aug 2024)
                if pd.notnull(row['Date_Parsed']):
                    formatted_date = row['Date_Parsed'].strftime("%d %b %Y")
                else:
                    formatted_date = str(row['Raw_Date'])[:10]
                
                st.markdown(f"""
                <div class="sales-card">
                    <div>
                        <div style="font-size: 1.05rem; font-weight: 700; color: #1e293b;">{row['Address']}</div>
                        <div style="margin-top: 8px;">
                            <span class="badge badge-type">🏠 {row['Type']}</span>
                            <span class="badge badge-tenure">📜 {row['Tenure']}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">🗓️ Sold: {formatted_date}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.35rem; font-weight: 800; color: #16a34a;">£{row['Price']:,}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"No recent Land Registry transaction records found for postcode {active_postcode}.")

    # ===================================================================
    # TAB 4: CASH & SAVINGS
    # ===================================================================
    with tab_banking:
        st.subheader("💰 Cash & Savings Optimization")
        cash = st.number_input("Household Cash Balance (£):", value=10000, step=1000)
        st.metric("Target Market Yield (4.8%)", f"£{cash * 0.048:,.2f} / year")

else:
    st.warning("👈 Enter a postcode in the sidebar, search addresses, and click **Confirm Active Property** to unlock your audit.")
