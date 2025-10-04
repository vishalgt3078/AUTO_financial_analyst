"""
QueryPlanner Agent - Breaks down analysis requests into actionable tasks
"""

import json
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from utils.state_management import FinancialAnalysisState
from config import Config

class QueryPlannerAgent:
    def __init__(self):
        config = Config()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_retries=3,
            api_key=config.gemini_api_key
        )
        
        self.planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior financial analyst and research planner. 
Your task is to create a comprehensive research plan for analyzing a company.

Break down the analysis into specific, actionable tasks. Consider:
1. Current stock performance and valuation metrics
2. Recent earnings and financial statements  
3. Industry comparisons and market position
4. Recent news and market sentiment
5. SEC filings and regulatory information

Return a JSON list of tasks with this structure:
[
  {{"task_type": "stock_data", "description": "Get current stock price and historical performance", "priority": 1}},
  {{"task_type": "earnings", "description": "Analyze latest quarterly earnings", "priority": 2}}
]

Task types should be: stock_data, earnings, news, sec_filing, industry_analysis

Focus on creating a practical, achievable research plan that will provide sufficient data for a comprehensive investment analysis."""),
            ("human", "Create a research plan to analyze {company_name} and provide a buy/sell recommendation. Make it practical and focused on essential information.")
        ])

    def run(self, state: FinancialAnalysisState) -> FinancialAnalysisState:
        try:
            chain = self.planning_prompt | self.llm
            response = chain.invoke({"company_name": state["company_name"]})
            
            response_content = response.content.strip()
            start_idx = response_content.find('[')
            end_idx = response_content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_content[start_idx:end_idx]
                tasks = json.loads(json_str)
            else:
                tasks = [
                    {"task_type": "stock_data", "description": f"Get current stock data for {state['company_name']}", "priority": 1},
                    {"task_type": "earnings", "description": f"Analyze financial statements for {state['company_name']}", "priority": 2},
                    {"task_type": "news", "description": f"Get recent financial news for {state['company_name']}", "priority": 3},
                    {"task_type": "sec_filing", "description": f"Review recent SEC filings for {state['company_name']}", "priority": 4}
                ]
            
            research_plan = [task["description"] for task in tasks]
            state["research_plan"] = research_plan
            state["messages"].append(AIMessage(content=f"Created research plan with {len(tasks)} tasks for {state['company_name']}"))
            
            print(f"✅ QueryPlanner: Created {len(tasks)} research tasks")
            
        except Exception as e:
            print(f"❌ QueryPlanner error: {str(e)}")
            state["research_plan"] = [
                f"Get stock data for {state['company_name']}",
                f"Analyze financials for {state['company_name']}",
                f"Get news for {state['company_name']}"
            ]
            state["messages"].append(AIMessage(content=f"Created fallback research plan"))
        
        return state

def query_planner(state: FinancialAnalysisState) -> FinancialAnalysisState:
    agent = QueryPlannerAgent()
    return agent.run(state)
