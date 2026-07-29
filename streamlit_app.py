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
    
    # 1. Standardize Postcode Format (Ensuring uppercase and correct single space)
    clean_postcode = postcode_input.strip().upper()
    if len(clean_postcode) >= 5 and " " not in clean_postcode:
        clean_postcode = f"{clean_postcode[:-3]} {clean_postcode[-3:]}"
    
    # 2. URL Encode space to %20
    encoded_postcode = urllib.parse.quote(clean_postcode)
    
    # 3. Correct HM Land Registry API Parameter: propertyAddress.postcode
    url = f"https://landregistry.data.gov.uk/data/ppi/transaction-record.json?propertyAddress.postcode={encoded_postcode}&_pageSize=50"
    
    try:
        response = requests.get(url, headers={'Accept': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            results = data.get('result', {}).get('items', [])
            
            if results:
                st.success(f"Found {len(results)} historic property transactions for {clean_postcode}!")
                
                records = []
                for item in results:
                    paon = item.get('propertyAddress', {}).get('paon', '')
                    saon = item.get('propertyAddress', {}).get('saon', '')
                    street = item.get('propertyAddress', {}).get('street', '')
                    
                    # Combine flat/house number & street
                    address_str = f"{saon} {paon} {street}".strip()
                    
                    records.append({
                        "Price": f"£{item.get('pricePaid', 0):,}",
                        "Date": item.get('transactionDate', 'N/A'),
                        "Address": address_str
                    })
                
                st.table(records)
            else:
                st.warning(f"No sales history returned by Land Registry for '{clean_postcode}'.")
        else:
            st.error(f"API returned status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
