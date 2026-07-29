# ===================================================================
    # TAB 3: LAND REGISTRY SALES HISTORY (NO GRAPH, CLEAN METRICS + CARDS)
    # ===================================================================
    with tab_sales:
        st.subheader("🏠 HM Land Registry Sold Price History")
        st.caption(f"Official record of registered property sales for postcode **{active_postcode}** (Source: HM Land Registry)")
        
        df_sales = fetch_land_registry_sales(active_postcode)
        
        if not df_sales.empty:
            # Key Postcode Metrics
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
            
            # Average Price by Property Type (Replaces Useless Line Chart)
            st.markdown("### 📊 Average Price by House Type")
            type_summary = df_sales.groupby('Type')['Price'].agg(['mean', 'count']).reset_index()
            type_cols = st.columns(len(type_summary))
            
            for idx, row in type_summary.iterrows():
                if idx < len(type_cols):
                    with type_cols[idx]:
                        st.metric(
                            label=f"{row['Type']} ({row['count']} sales)", 
                            value=f"£{int(row['mean']):,}"
                        )
            
            st.divider()
            st.markdown("### 📜 Registered Transactions")
            
            # Clean Cards List
            for _, row in df_sales.iterrows():
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
