import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="Golf App", layout="centered")
st.title("⛳ Golf App Cloud Test")

# 1. Direct pull from secrets
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
except Exception as secret_err:
    st.error("Missing Secrets configuration in Streamlit settings.")
    st.stop()

# 2. Setup database client
@st.cache_resource
def get_supabase_client(url_str, key_str) -> Client:
    return create_client(url_str, key_str)

supabase = get_supabase_client(url, key)

# --- SIGN UP INTERFACE (NO PASSWORD) ---
st.header("🔐 Player Sign Up Test")
name_input = st.text_input("Choose a Username:").strip().lower()

if st.button("Create Account"):
    # Safety Check: Only try to save if they actually typed a name
    if name_input:
        try:
            supabase.table("golf_profiles").insert({
                "username": name_input,
                "rounds": []
            }).execute()
            st.success(f"Success! Account for '{name_input.capitalize()}' is saved in the cloud!")
        except Exception as error:
            st.error(f"Database Error: {error}")
    else:
        st.warning("Please type a username first!")
