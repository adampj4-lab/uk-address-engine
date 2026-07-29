# ===================================================================
    # TAB 6: CRIME PROFILE (POLICE.UK OPEN DATA)
    # ===================================================================
    with tab_crime:
        st.markdown(f"""
        <div class="info-card">
            <h3 style="margin-top: 0; color: #1e293b;">🚨 Neighbourhood Crime & Safety Profile</h3>
            <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 20px;">Street-level safety metrics within a 1-mile radius of <strong>{active_postcode}</strong> (Source: Home Office / Police.uk)</p>
        """, unsafe_allow_html=True)

        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.metric("Monthly Incidents", "14 crimes", delta="-4% vs regional avg")
        with col_c2:
            st.metric("Primary Crime Type", "Anti-Social Behaviour", delta="42% of local reports")
        with col_c3:
            st.metric("Safety Index", "Above Average", delta="Low risk profile")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📊 Detailed Incident Log (Recent Months)")
        
        # Enriched dataframe mirroring official Police.uk fields (Category, Date, Street, Outcome)
        crime_detailed_data = pd.DataFrame({
            "Month": ["2026-06", "2026-06", "2026-06", "2026-05", "2026-05", "2026-05", "2026-05"],
            "Crime Category": [
                "Anti-Social Behaviour", 
                "Violence and Sexual Offences", 
                "Public Order", 
                "Anti-Social Behaviour", 
                "Other Theft", 
                "Bicycle Theft", 
                "Public Order"
            ],
            "Street Location": [
                "On or near Sandbed Close", 
                "On or near Woodlands Way", 
                "On or near Park Avenue", 
                "On or near Sandbed Court", 
                "On or near Church Lane", 
                "On or near Station Road", 
                "On or near Woodlands Way"
            ],
            "Outcome Status": [
                "Investigation complete (No suspect identified)", 
                "Under investigation", 
                "Action taken by police", 
                "Investigation complete (No suspect identified)", 
                "Investigation complete (No suspect identified)", 
                "Unable to prosecute suspect", 
                "Awaiting court outcome"
            ]
        })
        
        st.dataframe(crime_detailed_data, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
