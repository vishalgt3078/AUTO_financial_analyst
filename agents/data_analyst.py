"""
DataAnalyst Agent - The reasoning agent that analyzes raw data
"""

from datetime import datetime
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from utils.state_management import FinancialAnalysisState
from config import Config

class DataAnalystAgent:
    def __init__(self):
        config = Config()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_retries=3,
            api_key=config.gemini_api_key
        )
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior financial analyst with expertise in equity research and valuation.

Analyze the provided financial data and provide comprehensive insights. Structure your analysis with these sections:

1. EXECUTIVE SUMMARY
   - Key financial highlights
   - Current market position
   - Overall assessment

2. FINANCIAL HEALTH ASSESSMENT
   - Revenue trends and growth
   - Profitability metrics
   - Balance sheet strength
   - Cash flow analysis

3. VALUATION ANALYSIS
   - P/E ratio and valuation metrics
   - Price targets and fair value
   - Comparison to industry peers

4. GROWTH PROSPECTS
   - Revenue growth potential
   - Market expansion opportunities
   - Innovation and competitive advantages

5. RISK FACTORS
   - Market risks
   - Company-specific risks
   - Industry challenges

6. INVESTMENT RECOMMENDATION
   - Clear BUY/HOLD/SELL recommendation
   - Target price if applicable
   - Key reasons for recommendation

IMPORTANT INSTRUCTIONS:
- Use the EXACT currency symbol provided in the data (₹ for Indian stocks, $ for US stocks)
- Use CURRENT DATE: {current_date}
- Do NOT use any old dates like 2023 or October 26, 2023
- Use the exact market information provided (Indian Market vs International Market)
- Be specific with numbers and metrics from the provided data
- Include quantitative analysis where possible
- Focus on actionable insights for investors"""),
            ("human", """Analyze this financial data for {company_name}:

CURRENT DATE: {current_date}
MARKET: {market}
CURRENCY: {currency}

STOCK DATA SUMMARY:
{stock_summary}

ADDITIONAL DATA:
{additional_data}

Provide a comprehensive financial analysis with clear sections, specific metrics, and a definitive investment recommendation. Use the current date and proper currency symbols as specified above.""")
        ])

    def run(self, state: FinancialAnalysisState) -> FinancialAnalysisState:
        """
        This agent performs sophisticated analysis of the raw data.
        It looks for trends, calculates metrics, and identifies key insights.
        """
        print("📊 DataAnalyst: Starting data analysis...")
        
        raw_data = state.get("raw_data", {})
        
        try:
            # Prepare stock data summary
            stock_data = raw_data.get("stock_data", {})
            
            stock_summary = "No stock data available"
            
            if stock_data and "error" not in stock_data:
                info = stock_data.get("company_info", {})
                market = stock_data.get("market", "International Market")
                currency = stock_data.get("currency", "USD")
                
                # Format market cap properly
                market_cap = info.get('marketCap', 'N/A')
                if isinstance(market_cap, (int, float)) and market_cap > 0:
                    if market_cap >= 1e12:
                        market_cap_str = f"₹{market_cap/1e12:.2f}T" if currency == "INR" else f"${market_cap/1e12:.2f}T"
                    elif market_cap >= 1e9:
                        market_cap_str = f"₹{market_cap/1e9:.2f}B" if currency == "INR" else f"${market_cap/1e9:.2f}B"
                    else:
                        market_cap_str = f"₹{market_cap/1e6:.2f}M" if currency == "INR" else f"${market_cap/1e6:.2f}M"
                else:
                    market_cap_str = str(market_cap)
                
                stock_summary = f"""
Company: {info.get('longName', 'N/A')}
Current Price: {currency} {info.get('currentPrice', 'N/A')}
Market Cap: {market_cap_str}
P/E Ratio: {info.get('trailingPE', 'N/A')}
52-Week High: {currency} {info.get('fiftyTwoWeekHigh', 'N/A')}
52-Week Low: {currency} {info.get('fiftyTwoWeekLow', 'N/A')}
Revenue Growth: {info.get('revenueGrowth', 'N/A')}
Profit Margins: {info.get('profitMargins', 'N/A')}
Industry: {info.get('industry', 'N/A')}
Sector: {info.get('sector', 'N/A')}
Market: {market}
Currency: {currency}
Data Quality: {stock_data.get('data_quality', 'unknown')}
"""
            
            # Prepare additional data summary
            additional_data = """
SEC Filings: {sec_summary}
Recent News: {news_summary}
Alpha Vantage: {av_summary}
""".format(
                sec_summary=str(raw_data.get("sec_filings", ""))[:500] + "..." if len(str(raw_data.get("sec_filings", ""))) > 500 else str(raw_data.get("sec_filings", "")),
                news_summary=str(raw_data.get("news", ""))[:300] + "..." if len(str(raw_data.get("news", ""))) > 300 else str(raw_data.get("news", "")),
                av_summary=str(raw_data.get("alpha_vantage", ""))[:300] + "..." if len(str(raw_data.get("alpha_vantage", ""))) > 300 else str(raw_data.get("alpha_vantage", ""))
            )
            
            # Get market information and currency
            market = stock_data.get("market", "International Market")
            currency = stock_data.get("currency", "USD")
            current_date = datetime.now().strftime('%B %d, %Y')
            
            # Generate analysis using Gemini
            chain = self.analysis_prompt | self.llm
            response = chain.invoke({
                "company_name": state["company_name"],
                "stock_summary": stock_summary,
                "additional_data": additional_data,
                "current_date": current_date,
                "market": market,
                "currency": currency
            })
            
            # Store analysis results
            analysis_results = {
                "detailed_analysis": response.content,
                "timestamp": datetime.now().isoformat(),
                "data_sources_used": list(raw_data.keys())
            }
            
            state["analyzed_data"] = analysis_results
            state["messages"].append(AIMessage(content=f"Completed comprehensive analysis of {state['company_name']} using {len(raw_data)} data sources"))
            
            print("✅ DataAnalyst: Analysis completed successfully")
            
        except Exception as e:
            print(f"❌ DataAnalyst error: {str(e)}")
            state["analyzed_data"] = {
                "error": f"Analysis failed: {str(e)}",
                "fallback_analysis": f"Basic analysis for {state['company_name']}: Data collection completed, detailed analysis pending."
            }
            state["messages"].append(AIMessage(content=f"Analysis encountered issues, fallback analysis created"))
        
        return state

def data_analyst(state: FinancialAnalysisState) -> FinancialAnalysisState:
    agent = DataAnalystAgent()
    return agent.run(state)
