import os
from dataclasses import dataclass
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    def __init__(self):
        # Try environment variables first, then streamlit secrets, with fallback to empty string
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        self.alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        self.stock_news_api_key = os.getenv('STOCK_NEWS_API_KEY', '')
        
        # Try to get from streamlit secrets if not found in environment
        try:
            if not self.gemini_api_key:
                self.gemini_api_key = st.secrets.get('GEMINI_API_KEY', '')
            if not self.alpha_vantage_api_key:
                self.alpha_vantage_api_key = st.secrets.get('ALPHA_VANTAGE_API_KEY', '')
            if not self.stock_news_api_key:
                self.stock_news_api_key = st.secrets.get('STOCK_NEWS_API_KEY', '')
        except Exception:
            # If secrets are not available, use empty strings
            pass
        
    def is_configured(self):
        return bool(self.gemini_api_key and self.alpha_vantage_api_key)
