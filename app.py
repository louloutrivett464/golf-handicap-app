import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="Golf App", layout="centered")
st.title("⛳ Golf App Cloud Test")

# 1. HARDCODING THE DIRECT REST API URL (Bypassing Streamlit Secrets completely)
URL = "https://krcvsbzryafkwwiwmfc.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtyY3N2c2J6cnlhZmt3d2l3bWZjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDMwMzYzNywiZXhwIjoyMDk1ODc5NjM3fQ.FQ2Muw8oaUJuS32jqzJbieK-BGx5FGAZR3uZLmL2lpc"

# 2. Build direct client connection bridge
supabase: Client = create_client(URL, KEY)

# --- SIGN UP INTERFACE (NO PASSWORD) ---
st.header("🔐 Player Sign Up Test")
name_input = st.text_input("Choose a Username:").strip().lower()

if st.button("Create Account"):
    if name_input:
        try:
            # 3. Direct execution write payload
            supabase.table("golf_profiles").insert({
                "username": name_input,
                "rounds": []
            }).execute()
            st.success(f"Success! Account for '{name_input.capitalize()}' is saved in the cloud!")
        except Exception as error:
            st.error(f"Database Error: {error}")
    else:
        st.warning("Please type a username first!")
