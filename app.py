import streamlit as st
from st_supabase_connection import SupabaseConnection

st.set_page_config(page_title="Golf App", layout="centered")
st.title("⛳ Golf App Cloud Test")

# Initialize connection using official Streamlit Cloud Secrets parameters
def init_connection():
    return st.connection("supabase", type=SupabaseConnection)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Connection Setup Error: {e}")

# --- SIGN UP INTERFACE ---
st.header("🔐 Player Sign Up Test")
name_input = st.text_input("Choose a Username:").strip().lower()
password_input = st.text_input("Choose a Password:", type="password")

if st.button("Create Account"):
    if name_input and password_input:
        try:
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
