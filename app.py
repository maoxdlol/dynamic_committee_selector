import streamlit as st
import requests
import urllib

API_URL = st.secrets["api_url"] # replace with your API
BASE_FORM = st.secrets["base_form"]

st.set_page_config(page_title="Committee Selector", layout="centered")

st.title("Form D Submission Link Generation")
# ---------- Session state initialization ----------
if "standards_body_list" not in st.session_state:
    st.session_state.standards_body_list = []

if "intl_committee_list" not in st.session_state:
    st.session_state.intl_committee_list = []

if "local_committee_list" not in st.session_state:
    st.session_state.local_committee_list = []

if "standard_body" not in st.session_state:
    st.session_state.standard_body = ""

if "selected_intl_committee" not in st.session_state:
    st.session_state.selected_intl_committee = ""

if "selected_local_committee" not in st.session_state:
    st.session_state.selected_local_committee = ""

def add_selection():
    if (
        st.session_state.standard_body_select
        and st.session_state.intl_committee_select
        and st.session_state.local_committee_select
    ):
        st.session_state.standards_body_list.append(
            st.session_state.standard_body_select
        )
        st.session_state.intl_committee_list.append(
            st.session_state.intl_committee_select
        )
        st.session_state.local_committee_list.append(
            st.session_state.local_committee_select
        )

        # Reset widget values SAFELY
        st.session_state.standard_body_select = ""
        st.session_state.intl_committee_select = ""
        st.session_state.local_committee_select = ""

def clear_selections():
    # Clear stored lists
    st.session_state.standards_body_list.clear()
    st.session_state.intl_committee_list.clear()
    st.session_state.local_committee_list.clear()

    # Reset dropdown widgets
    st.session_state.standard_body_select = ""
    st.session_state.intl_committee_select = ""
    st.session_state.local_committee_select = ""


# ---------- Helper function ----------
@st.cache_data(ttl=60)
def fetch_options(mode):
    payload = {
        "method": "retrieve",
        "mode": mode
    }

    r = requests.post(API_URL, json=payload, timeout=5)
    r.raise_for_status()
    return r.json()["data"]


# ---------- Dropdown: Standard body ----------
st.session_state.standard_body = st.selectbox(
    "Select standard body",
    ["", "ISO", "IEC"],
    key="standard_body_select"
)

committee_options = None
local_committee_options = None

# ---------- Conditional dropdowns ----------
if st.session_state.standard_body:
    committee_mode = (
        "iso_committee"
        if st.session_state.standard_body == "ISO"
        else "iec_committee"
    )

    try:
        committee_options = fetch_options(committee_mode)
        local_committee_options = fetch_options("local_committee")
    except Exception as e:
        st.error(f"Failed to load options: {e}")
        st.stop()

    st.session_state.selected_intl_committee = st.selectbox(
        "International Committee",
        committee_options,
        key="intl_committee_select"
    )

    st.session_state.selected_local_committee = st.selectbox(
        "Local Committee",
        local_committee_options,
        key="local_committee_select"
    )

    # ---------- Add selection button ----------
    st.button(
        "Add selection",
        on_click=add_selection
    )


# ---------- Display current selections ----------
if st.session_state.standards_body_list:
    st.subheader("Current selections")
    for i in range(len(st.session_state.standards_body_list)):
        st.write(
            f"{i+1}. "
            f"{st.session_state.standards_body_list[i]} | "
            f"{st.session_state.intl_committee_list[i]} | "
            f"{st.session_state.local_committee_list[i]}"
        )

st.button(
    "Clear all selections",
    on_click=clear_selections
)

# ---------- Generate link ----------
if st.button("Generate link"):
    if not st.session_state.standards_body_list:
        st.warning("No selections added yet.")
    else:
        isoiec_prefill_id = "6948af700fed467dab55d79c"
        intl_comm_prefill_id = "6948af7ce7c2e6b0a4c41e5f"
        local_comm_prefill_id = "6948af875e7787d996ddda2d"

        # Join lists with |
        encoded_standard_body = urllib.parse.quote(
            ",".join(st.session_state.standards_body_list)
        )
        encoded_intl_committee = urllib.parse.quote(
            ",".join(st.session_state.intl_committee_list)
        )
        encoded_local_committee = urllib.parse.quote(
            ",".join(st.session_state.local_committee_list)
        )

        encoded_link = (
            f"{BASE_FORM}?"
            f"{isoiec_prefill_id}={encoded_standard_body}&"
            f"{intl_comm_prefill_id}={encoded_intl_committee}&"
            f"{local_comm_prefill_id}={encoded_local_committee}"
        )

        st.subheader("Generated link")
        st.write(encoded_link)