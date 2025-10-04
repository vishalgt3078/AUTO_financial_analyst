"""
DataFetcher Agent - Specialized tool agent for different data types
"""
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from sec_edgar_api import EdgarClient
import requests
import json
from typing import Dict, Any
from langchain_core.messages import AIMessage
from utils.state_management import FinancialAnalysisState
from config import Config

class DataFetcherAgent:
    def __init__(self):
        config = Config()
        self.alpha_ts = TimeSeries(key=config.alpha_vantage_api_key, output_format='pandas')
        self.alpha_fd = FundamentalData(key=config.alpha_vantage_api_key, output_format='pandas')
        self.edgar_client = EdgarClient(user_agent="Financial Analyst Bot admin@example.com")
        self.stock_news_api_key = getattr(config, 'stock_news_api_key', '')

    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch comprehensive stock data using yfinance with Indian stock support"""
        try:
            # Handle Indian stocks - add .NS suffix if not present
            original_symbol = symbol
            if not any(suffix in symbol.upper() for suffix in ['.NS', '.BO', '.NSE', '.BSE']):
                # Try with .NS suffix for Indian stocks
                indian_symbol = f"{symbol}.NS"
                print(f"🔍 Trying Indian stock format: {indian_symbol}")
                ticker = yf.Ticker(indian_symbol)
                info = ticker.info
                
                # Check if we got good data
                if info and len(info) > 50 and info.get('currentPrice'):
                    symbol = indian_symbol
                    print(f"✅ Found data with .NS suffix")
                else:
                    # Fall back to original symbol
                    ticker = yf.Ticker(original_symbol)
                    info = ticker.info
            else:
                ticker = yf.Ticker(symbol)
                info = ticker.info
            
            hist = ticker.history(period="1y")
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cash_flow
            
            # Validate data quality
            if not info or len(info) < 10:
                return {"error": f"Insufficient data for {original_symbol}. Try using .NS suffix for Indian stocks (e.g., RELIANCE.NS)"}
            
            # Ensure we have essential data
            essential_fields = ['currentPrice', 'marketCap', 'symbol', 'sector', 'industry']
            missing_fields = [field for field in essential_fields if field not in info or info[field] is None]
            
            if missing_fields:
                print(f"⚠️ Missing essential fields for {symbol}: {missing_fields}")
            
            # Add market information
            market_info = "Indian Market" if ".NS" in symbol else "International Market"
            
            return {
                "symbol": symbol,
                "original_symbol": original_symbol,
                "company_info": info,
                "price_history": hist,
                "financials": financials,
                "balance_sheet": balance_sheet,
                "cash_flow": cash_flow,
                "current_price": info.get('currentPrice', 'N/A'),
                "market_cap": info.get('marketCap', 'N/A'),
                "pe_ratio": info.get('trailingPE', 'N/A'),
                "data_quality": "good" if len(missing_fields) == 0 else "partial",
                "market": market_info,
                "currency": info.get('currency', 'INR' if '.NS' in symbol else 'USD')
            }
        except Exception as e:
            return {"error": f"Failed to fetch stock data for {original_symbol}: {str(e)}. For Indian stocks, try using .NS suffix (e.g., RELIANCE.NS)"}

    def get_alpha_vantage_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch additional data from Alpha Vantage"""
        try:
            overview_data, _ = self.alpha_fd.get_company_overview(symbol)
            daily_data, _ = self.alpha_ts.get_daily(symbol, outputsize='compact')
            
            return {
                "overview": overview_data,
                "daily_prices": daily_data,
                "source": "alpha_vantage"
            }
        except Exception as e:
            return {"error": f"Alpha Vantage API error: {str(e)}"}

    def get_sec_filings(self, symbol: str) -> Dict[str, Any]:
        """Fetch recent SEC filings"""
        try:
            company_tickers = self.edgar_client.get_company_tickers()
            
            cik = None
            for ticker_data in company_tickers.values():
                if ticker_data['ticker'] == symbol:
                    cik = str(ticker_data['cik_str']).zfill(10)
                    break
            
            if not cik:
                return {"error": f"Could not find CIK for symbol {symbol}"}
            
            submissions = self.edgar_client.get_submissions(cik=cik)
            
            important_forms = ['10-K', '10-Q', '8-K', 'DEF 14A']
            recent_filings = []
            
            if "filings" in submissions and "recent" in submissions["filings"]:
                forms = submissions["filings"]["recent"]["form"]
                dates = submissions["filings"]["recent"]["filingDate"]
                accession = submissions["filings"]["recent"]["accessionNumber"]
                
                for i, form in enumerate(forms[:20]):  # Last 20 filings
                    if form in important_forms:
                        recent_filings.append({
                            "form": form,
                            "filing_date": dates[i],
                            "accession_number": accession[i]
                        })
            
            return {
                "company_name": submissions.get("name", "Unknown"),
                "cik": cik,
                "recent_filings": recent_filings,
                "source": "sec_edgar"
            }
        except Exception as e:
            return {"error": f"SEC EDGAR API error: {str(e)}"}

    def get_financial_news(self, company_name: str) -> Dict[str, Any]:
        """Fetch recent financial news using free sources"""
        try:
            if self.stock_news_api_key and self.stock_news_api_key != "YOUR_STOCK_NEWS_API_KEY_HERE":
                url = f"https://stocknewsapi.com/api/v1?tickers={company_name}&items=10&token={self.stock_news_api_key}"
                response = requests.get(url)
                if response.status_code == 200:
                    return response.json()
            
            # Fallback to a simple web search approach (demo purposes)
            return {
                "message": f"News search for {company_name} - API key not configured",
                "sample_headlines": [
                    f"{company_name} reports quarterly earnings",
                    f"Analysts update {company_name} price targets",
                    f"{company_name} market performance analysis"
                ]
            }
        except Exception as e:
            return {"error": f"News fetch error: {str(e)}"}

    def run(self, state: FinancialAnalysisState) -> FinancialAnalysisState:
        """
        This agent specializes in fetching data from multiple sources.
        It's a tool agent with access to different financial APIs.
        """
        print("🔍 DataFetcher: Starting data collection...")
        
        if "raw_data" not in state:
            state["raw_data"] = {}
        
        company_name = state["company_name"]
        symbol = company_name.upper()  # Assume company name is the ticker for now
        
        # Fetch stock data using yfinance
        print(f"📊 Fetching stock data for {symbol}...")
        stock_data = self.get_stock_data(symbol)
        state["raw_data"]["stock_data"] = stock_data
        
        # Fetch Alpha Vantage data
        print(f"📈 Fetching Alpha Vantage data for {symbol}...")
        av_data = self.get_alpha_vantage_data(symbol)
        state["raw_data"]["alpha_vantage"] = av_data
        
        # Fetch SEC filings
        print(f"📋 Fetching SEC filings for {symbol}...")
        sec_data = self.get_sec_filings(symbol)
        state["raw_data"]["sec_filings"] = sec_data
        
        # Fetch financial news
        print(f"📰 Fetching financial news for {company_name}...")
        news_data = self.get_financial_news(company_name)
        state["raw_data"]["news"] = news_data
        
        # Update messages
        data_summary = f"Collected data from {len(state['raw_data'])} sources for {company_name}"
        state["messages"].append(AIMessage(content=data_summary))
        
        print(f"✅ DataFetcher: Completed data collection from {len(state['raw_data'])} sources")
        
        return state

def data_fetcher(state: FinancialAnalysisState) -> FinancialAnalysisState:
    agent = DataFetcherAgent()
    return agent.run(state)
