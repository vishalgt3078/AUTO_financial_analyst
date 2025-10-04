"""
ReportWriter Agent - Synthesizes analysis into professional reports
"""

from datetime import datetime
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from utils.state_management import FinancialAnalysisState
from config import Config

class ReportWriterAgent:
    def __init__(self):
        config = Config()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_retries=3,
            api_key=config.gemini_api_key
        )
        
        self.report_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior equity research analyst at a top-tier investment bank.

Create a professional investment research report with the following structure:

1. EXECUTIVE SUMMARY
   - Company overview and key highlights
   - Investment thesis in 2-3 sentences
   - Key financial metrics summary

2. INVESTMENT RECOMMENDATION
   - Clear BUY/HOLD/SELL recommendation
   - Target price with rationale
   - Risk/reward assessment
   - Time horizon for the recommendation

3. FINANCIAL ANALYSIS
   - Revenue and profitability trends
   - Balance sheet strength
   - Cash flow analysis
   - Key financial ratios

4. GROWTH PROSPECTS
   - Market opportunities
   - Competitive advantages
   - Innovation pipeline
   - Expansion potential

5. RISK FACTORS
   - Market risks
   - Company-specific risks
   - Regulatory risks
   - Mitigation strategies

6. VALUATION
   - Valuation methodology
   - Peer comparison
   - Price target calculation
   - Sensitivity analysis

7. CONCLUSION
   - Summary of key points
   - Final recommendation
   - Next steps for investors

IMPORTANT INSTRUCTIONS:
- Use the EXACT currency symbol provided in the analysis (₹ for Indian stocks, $ for US stocks)
- Use the CURRENT DATE: {current_date}
- Do NOT use any old dates like 2023 or October 26, 2023
- Use the exact market information provided (Indian Market vs International Market)
- Include specific metrics and numbers from the analysis
- Use professional language suitable for institutional investors"""),
            ("human", """Create a professional investment research report for {company_name} based on this analysis:

CURRENT DATE: {current_date}
MARKET INFORMATION: {market_info}
CURRENCY: {currency}

DETAILED ANALYSIS:
{analysis}

RESEARCH PLAN COMPLETED:
{research_plan}

Generate a comprehensive, well-structured report with clear sections, specific metrics, and a definitive investment recommendation with target price. Use the current date and proper currency symbols as specified above.""")
        ])

    def run(self, state: FinancialAnalysisState) -> FinancialAnalysisState:
        """
        This agent creates the final professional report with buy/sell recommendations.
        It synthesizes all the analysis into a coherent, actionable report.
        """
        print("📝 ReportWriter: Generating final report...")
        
        try:
            analyzed_data = state.get("analyzed_data", {})
            
            analysis_content = analyzed_data.get("detailed_analysis", "No detailed analysis available")
            research_plan = ", ".join(state.get("research_plan", []))
            
            # Get market information and currency
            raw_data = state.get("raw_data", {})
            stock_data = raw_data.get("stock_data", {})
            market_info = stock_data.get("market", "International Market")
            currency = stock_data.get("currency", "USD")
            
            # Get current date
            current_date = datetime.now().strftime('%B %d, %Y')
            
            # Generate report using Gemini
            chain = self.report_prompt | self.llm
            response = chain.invoke({
                "company_name": state["company_name"],
                "analysis": analysis_content,
                "research_plan": research_plan,
                "current_date": current_date,
                "market_info": market_info,
                "currency": currency
            })
            
            # Create final report with proper date formatting
            current_date = datetime.now()
            formatted_date = current_date.strftime('%B %d, %Y')
            
            # Get market information if available
            raw_data = state.get("raw_data", {})
            stock_data = raw_data.get("stock_data", {})
            market_info = stock_data.get("market", "International Market")
            currency = stock_data.get("currency", "USD")
            
            final_report = f"""
Investment Research Report: {state['company_name']}

Generated on: {formatted_date}
Analysis Date: {current_date.strftime('%Y-%m-%d')}
Analysis Type: Comprehensive Multi-Source Analysis
Market: {market_info}
Currency: {currency}
Data Sources: {", ".join(raw_data.keys())}

---

{response.content}

---

Disclaimer: This analysis is generated by an AI system for educational purposes. 
Please consult with qualified financial advisors before making investment decisions.
Generated on {formatted_date} at {current_date.strftime('%H:%M:%S')} UTC.
"""
            
            state["final_report"] = final_report
            state["messages"].append(AIMessage(content=f"Generated comprehensive investment report for {state['company_name']}"))
            
            print("✅ ReportWriter: Professional report generated")
            
        except Exception as e:
            print(f"❌ ReportWriter error: {str(e)}")
            state["final_report"] = f"""
Investment Research Report: {state['company_name']}

Status: Report generation encountered technical difficulties.
Error: {str(e)}

Available Data: Analysis completed for data sources: {", ".join(state.get("raw_data", {}).keys())}

Please review the raw analysis data and try regenerating the report.
"""
            state["messages"].append(AIMessage(content=f"Report generation failed, error report created"))
        
        return state

def report_writer(state: FinancialAnalysisState) -> FinancialAnalysisState:
    agent = ReportWriterAgent()
    return agent.run(state)
