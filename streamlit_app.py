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
                
                # Indicative formula
                calc_fee = round((current_bill * 0.80) * months_left, 2)
                
                # User Override Toggle
                override_fee = st.checkbox("I know my exact provider exit fee quote")
                
                if override_fee:
                    est_exit_fee = st.number_input("Enter Exact Exit Fee (£):", min_value=0.0, value=65.00, step=5.0)
                else:
                    est_exit_fee = calc_fee
                    st.caption(f"⏱️ **Contract Expiry:** {expiry_date.strftime('%d/%m/%Y')} (~{months_left} months remaining). Indicative exit fee: **~£{est_exit_fee:.2f}**")
        else:
            with col_in5:
                st.write("")
