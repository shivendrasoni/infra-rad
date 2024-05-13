from st_supabase_connection import SupabaseConnection
import streamlit as st
from dotenv import load_dotenv

# Initialize connection.
def get_connection():

    st_supabase_client = st.connection(
        name="supabase",
        type=SupabaseConnection
    )

    return st_supabase_client
