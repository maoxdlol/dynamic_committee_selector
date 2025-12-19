import streamlit as st
import requests
import urllib

API_URL = "https://0twmzxyly2.execute-api.ap-southeast-2.amazonaws.com/stage1"  # replace with your API

st.set_page_config(page_title="Committee Selector", layout="centered")

st.title("Form D Submission Link Generation")

# ---------- Helper function ----------
@st.cache_data(ttl=300)
def fetch_options(mode):
    payload = {
        "method": "retrieve",
        "mode": mode
    }

    r = requests.post(
        API_URL,
        json=payload,
        timeout=5
    )
    r.raise_for_status()
    return r.json()["data"]

# ---------- First dropdown ----------
standard_body = st.selectbox(
    "Select standard body",
    ["","ISO", "IEC"]
)

# ---------- Conditional dropdowns ----------
committee_options = None

if standard_body:
    if standard_body == "ISO":
        committee_mode = "iso_committee"
    else:
        committee_mode = "iec_committee"

    try:
        committee_options = fetch_options(committee_mode)
        local_committee_options = fetch_options("local_committee")
    except Exception as e:
        st.error(f"Failed to load options: {e}")
        st.stop()

    # ---------- Dynamic dropdowns ----------
    selected_intl_committee = st.selectbox(
        "International Committee",
        committee_options
    )

    selected_local_committee = st.selectbox(
        "Local Committee",
        local_committee_options
    )

    #custom Form D submission form link on FormSG
    base_link = "https://form.gov.sg/69200e20995dfac1747fc375"
    intl_comm_prefill_id = "6944c11aabb49d6db51542ec"
    local_comm_prefill_id = "692018fd6d7b136259eb350c"
    html_encoded_intl_committee_name = urllib.parse.quote(selected_intl_committee)
    html_encoded_local_committee_name = urllib.parse.quote(selected_local_committee)
    encoded_link = f"{base_link}?{intl_comm_prefill_id}={html_encoded_intl_committee_name}&{local_comm_prefill_id}={html_encoded_local_committee_name}"

    # ---------- Output selections ----------
    st.header("Form D submission link will be generated below")
    st.write("Please ensure correct local committee is mapped to international committee.")
    st.write("Please submit Form D at this link", encoded_link)
