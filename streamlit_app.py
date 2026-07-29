import streamlit as st
import requests

# Page Configuration
st.set_page_config(page_title="Address Engine", page_icon="🏠", layout="centered")

st.title("UK Address & Property Engine 🏠")
st.write("Scan property transaction data directly from HM Land Registry Open Data.")

# User Input
postcode = st.text_input("Enter a UK Postcode:", "YO43 4EG")

if st.button("Scan Address"):
    st.info(f"Scanning data for {postcode}...")
    
    # Clean postcode format for API
    formatted_postcode = postcode.replace(" ", "")
    
    # Land Registry API Query
    url = f"https://landregistry.data.gov.uk/data/ppi/transaction-record.json?postcode={formatted_postcode}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results = data.get('result', {}).get('items', [])
            
            if results:
                st.success(f"Found {len(results)} historic property transactions!")
                
                # Format into a clean summary list
                records = []
                for item in results[:10]:  # Show top 10
                    paon = item.get('propertyAddress', {}).get('paon', '')
                    street = item.get('propertyAddress', {}).get('street', '')
                    records.append({
                        "Price": f"£{item.get('pricePaid', 0):,}",
                        "Date": item.get('transactionDate', 'N/A'),
                        "Address": f"{paon} {street}".strip()
                    })
                
                st.table(records)
            else:
                st.warning("No sales history found for this specific postcode.")
        else:
            st.error("API error retrieving Land Registry data.")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
