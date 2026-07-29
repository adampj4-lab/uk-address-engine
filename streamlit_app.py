# ===================================================================
    # TAB 2: UNIFIED ENERGY & EPC OPTIMIZATION (INDEPENDENT FUELS)
    # ===================================================================
    with tab_energy:
        st.subheader("⚡ Property Efficiency & Tariff Audit")
        st.caption(f"Real-time building diagnostics & multi-fuel tariff optimizer for **{active_property}**")
        
        epc = fetch_real_epc_data(active_postcode, active_property)
        
        # 1. Building Infrastructure Cards
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
            st.metric("Est. Building Running Cost", f"£{epc['est_annual_bill']:,} / yr")

        st.divider()
        
        # 2. Building Efficiency Diagnostics
        st.markdown("### 🔍 Infrastructure Diagnostics")
        col_det1, col_det2 = st.columns(2)
        with col_det1:
            st.write(f"🔥 **Main Heating:** {epc['heating']}")
            st.write(f"🪟 **Glazing:** {epc['glazing']}")
        with col_det2:
            st.write(f"💡 **Lighting Efficiency:** {epc['lighting']}")
            st.write(f"☀️ **Solar Array Potential:** Suitable for 3.8 kWp (~£450/yr generation savings)")

        st.divider()

        # 3. Interactive Multi-Fuel Energy Audit
        st.markdown("### 💰 Household Fuel & Tariff Audit")
        
        fuel_setup = st.radio("Household Energy Supply Setup:", ["Electricity & Gas (Split/Separate Suppliers)", "Electricity Only (All-Electric / Heat Pump)", "Gas Only"], horizontal=True)
        
        has_ev = st.checkbox("🔌 I have a Plug-In Hybrid (PHEV) or Electric Vehicle (EV)", value=True)

        elec_supplier, elec_bill, gas_supplier, gas_bill = "Octopus Energy", 90.0, "Octopus Energy", 55.0

        if "Electricity" in fuel_setup:
            st.markdown("#### ⚡ Electricity Details")
            col_el1, col_el2, col_el3 = st.columns(3)
            with col_el1:
                elec_supplier = st.selectbox("Electricity Supplier:", ["Octopus Energy", "British Gas", "E.ON Next", "OVO Energy", "EDF Energy", "Other"], key="elec_sup")
            with col_el2:
                elec_bill = st.number_input("Electricity Monthly Bill (£):", min_value=10.0, max_value=600.0, value=90.0, step=5.0, key="elec_cost")
            with col_el3:
                elec_tariff_type = st.selectbox("Electricity Tariff Type:", ["EV / PHEV Smart Tariff (e.g. Intelligent Octopus Go)", "Standard Variable (Price Cap)", "12M Fixed Rate"], key="elec_type")

        if "Gas" in fuel_setup:
            st.markdown("#### 🔥 Gas Details")
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                gas_supplier = st.selectbox("Gas Supplier:", ["Octopus Energy", "British Gas", "E.ON Next", "OVO Energy", "EDF Energy", "Other"], key="gas_sup")
            with col_g2:
                gas_bill = st.number_input("Gas Monthly Bill (£):", min_value=10.0, max_value=600.0, value=55.0, step=5.0, key="gas_cost")
            with col_g3:
                gas_tariff_type = st.selectbox("Gas Tariff Type:", ["Standard Variable (Price Cap)", "12M Fixed Rate"], key="gas_type")

        total_annual_spend = (elec_bill if "Electricity" in fuel_setup else 0) * 12 + (gas_bill if "Gas" in fuel_setup else 0) * 12
        
        st.markdown("---")
        st.markdown("### 🏷️ Market Tariff Comparison (Independent Fuel Matches)")
        
        tariffs = []
        
        if has_ev:
            tariffs.append({
                "Name": "Intelligent Octopus Go (EV/PHEV)",
                "Fuel": "Electricity Only",
                "AnnualCost": 890.00,
                "Perks": "7p–8p/kWh Overnight Charging Window / Smart Dispatch",
                "Fit": "Optimal for Omoda 9, EVs, or battery storage"
            })
        
        tariffs.extend([
            {
                "Name": "Octopus Fixed 12M (Elec + Gas Split)",
                "Fuel": "Elec & Gas",
                "AnnualCost": 1520.00,
                "Perks": "100% Green Electricity / No Exit Fees",
                "Fit": "Best for price stability across both fuels"
            },
            {
                "Name": "E.ON Next Fixed 15M",
                "AnnualCost": 1545.00,
                "Fuel": "Elec & Gas",
                "Perks": "Fixed unit rates through winter",
                "Fit": "Long-term protection"
            }
        ])
        
        for t in tariffs:
            annual_diff = total_annual_spend - t['AnnualCost']
            monthly_saving = annual_diff / 12
            
            if annual_diff > 0:
                t_financial = f"Save £{annual_diff:.2f}/yr (£{monthly_saving:.2f}/mo)"
                t_color = "#16a34a"
            else:
                t_financial = f"+£{abs(annual_diff):.2f}/yr compared to combined bill"
                t_color = "#d97706"

            st.markdown(f"""
            <div class="deal-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="deal-title">{t['Name']}</div>
                        <div style="margin-top: 6px;">
                            <span class="badge">{t['Fuel']}</span>
                            <span class="badge badge-speed">⚡ {t['Fit']}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">🎁 {t['Perks']}</div>
                    </div>
                    <div style="text-align: right;">
                        <div class="deal-price">£{t['AnnualCost']/12:.2f} <span style="font-size: 0.8rem; font-weight: normal; color: #64748b;">/mo</span></div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: {t_color};">{t_financial}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
