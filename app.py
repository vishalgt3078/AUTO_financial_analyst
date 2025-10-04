import streamlit as st
from components.ui_components import render_dashboard

def main():
    st.set_page_config(page_title="Autonomous Financial Analyst", layout="wide")
    st.title("📊 Autonomous Financial Analyst")
    render_dashboard()

if __name__ == "__main__":
    main()
