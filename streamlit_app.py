import streamlit as st
import requests
import re

# Ideal Postcodes Key
IDEAL_POSTCODES_API_KEY = "ak_test"

# Natural sorting helper
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# -------------------------------------------------------------------
# CACHED API CALL: Saves results locally so repeat postcodes cost 0 credits
# -------------------------------------------------------------------
@st.cache_data(ttl=86400)  # Caches results for 24 hours (86,400 seconds)
def get_cached_addresses(clean_postcode):
    url = f"https://api.ideal-postcodes.co.uk/v1/postcodes/{clean_postcode}?api_key={IDEAL_POSTCODES_API_KEY}"
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
    return []

# -------------------------------------------------------------------
# CALLBACK FUNCTION: Executes when "Find Addresses" button is clicked
# -------------------------------------------------------------------
def fetch_addresses():
    raw_pc = st.session_state.postcode_input.strip().upper()
    if len(raw_pc) >= 5 and " " not in raw_pc:
        raw_pc = f"{raw_pc[:-3]} {raw_pc[-3:]}"
    
    st.session_state['scanned_postcode'] = raw_pc
    clean_pc = raw_pc.replace(" ", "")
    
    # Calls the cached function
    address_list = get_cached_addresses(clean_pc)
    
    if address_list:
        st.session_state['address_list'] = address_list
    else:
        st.error("Invalid Postcode or API limit reached.")
