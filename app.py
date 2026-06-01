# Cache Busting Version 1.0.1 - Direct Connection Run
import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="Golf App", layout="centered")
st.title("⛳ Golf App Cloud Test")

# 1. Pull variables directly from Streamlit Secrets
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
except Exception as secret_err:
    st.error(f"Secrets Retrieval Error: {secret_err}")
    st.stop()

# 2. Build the direct connection client manually
@st.cache_resource
def get_supabase_client(url_str, key_str) -> Client:
    return create_client(url_str, key_str)

try:
    supabase = get_supabase_client(url, key)
except Exception as conn_err:
    st.error(f"Connection Initialization Error: {conn_err}")
    st.stop()

# --- SIGN UP INTERFACE ---
st.header("🔐 Player Sign Up Test")
name_input = st.text_input("Choose a Username:").strip().lower()
password_input = st.text_input("Choose a Password:", type="password")

if st.button("Create Account"):
    if name_input and password_input:
        try:
            # 3. Direct execution write payload
            supabase.table("golf_profiles").insert({
                "username": name_input,
                "password": password_input,
                "rounds": []
            }).execute()
            st.success(f"Success! Account for '{name_input.capitalize()}' is saved in the cloud!")
        except Exception as error:
            st.error(f"Database Error: {error}")
    else:
        st.warning("Please fill in both fields.")
