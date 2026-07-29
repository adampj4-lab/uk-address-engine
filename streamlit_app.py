import streamlit as st
import requests
import urllib.parse

# Page Configuration
st.set_page_config(page_title="Address Engine", page_icon="🏠", layout="centered")

st.title("UK Address & Property Engine 🏠")
st.write("Scan property transaction data directly from HM Land Registry Open Data.")

# User Input
postcode_input = st.text_input("Enter a UK Postcode:", "YO43 4EG")

if st.button("Scan Address"):
    st.info(f"Scanning data for {postcode_input}...")
    
    # 1. Standardize Postcode Format (e.g., ensure correct spacing: YO43 4EG)
    clean_postcode = postcode_input.strip().upper()
    if len(clean_postcode) >= 5 and " " not in clean_postcode:
        # Insert space before the last 3 characters if missing
        clean_postcode = f"{clean_postcode[:-3]} {clean_postcode[-3:]}"
    
    # 2. URL Encode the postcode (turns 'YO43 4EG' into 'YO43%204EG')
    encoded_postcode = urllib.parse.quote(clean_postcode)
    
    # Land Registry API Endpoint
    url = f"https://landregistry.data.gov.uk/data/ppi/transaction-record.json?postcode={encoded_postcode}"
    
    try:
        response = requests.get(url, headers={'Accept': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            results = data.get('result', {}).get('items', [])
            
            if results:
                st.success(f"Found {len(results)} historic property transactions for {clean_postcode}!")
                
                records = []
                for item in results[:10]:
                    paon = item.get('propertyAddress', {}).get('paon', '')
                    street = item.get('propertyAddress', {}).get('street', '')
                    records.append({
                        "Price": f"£{item.get('pricePaid', 0):,}",
                        "Date": item.get('transactionDate', 'N/A'),
                        "Address": f"{paon} {street}".strip()
                    })
                
                st.table(records)
            else:
                st.warning(f"No sales history returned by Land Registry for '{clean_postcode}'. Try a nearby postcode like 'LS1 4AP' or 'YO43 3GA' to test.")
        else:
            st.error(f"API returned status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
