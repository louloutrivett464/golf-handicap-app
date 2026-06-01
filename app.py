import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Golf App", layout="centered")
st.title("⛳ Golf App Cloud Test")

# --- DIRECT DATABASE CONNECTION ---
URL = "https://supabase.co"
KEY = "sb_secret_Now3Qzgc144fpYVlVC-alg_bhDfKzdX"

try:
    supabase = create_client(URL, KEY)
except Exception as e:
    st.error(f"Connection Setup Error: {e}")

# --- SIMPLE SIMPLIFIED SIGN UP ---
st.header("🔐 Player Sign Up Test")
name_input = st.text_input("Choose a Username:").strip().lower()
password_input = st.text_input("Choose a Password:", type="password")

if st.button("Create Account"):
    if name_input and password_input:
        try:
            # Directly inserts a clean row into your Supabase table
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
