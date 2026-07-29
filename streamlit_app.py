import re

# Custom natural sorting function to fix string ordering (e.g., 1, 2, 10 instead of 1, 10, 2)
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def fetch_addresses():
    raw_pc = st.session_state.postcode_input.strip().upper()
    if len(raw_pc) >= 5 and " " not in raw_pc:
        raw_pc = f"{raw_pc[:-3]} {raw_pc[-3:]}"
    
    st.session_state['scanned_postcode'] = raw_pc
    clean_pc = raw_pc.replace(" ", "")
    
    url = f"https://api.ideal-postcodes.co.uk/v1/postcodes/{clean_pc}?api_key={IDEAL_POSTCODES_API_KEY}"
    
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
            
            # NATURAL SORTING APPLIED HERE
            st.session_state['address_list'] = sorted(addresses, key=natural_sort_key)
        else:
            st.error("Invalid Postcode or API limit reached.")
    except Exception as e:
        st.error(f"Error connecting to Address API: {e}")
