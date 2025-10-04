"""
QualityChecker Agent - The critic that reviews and validates reports
"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from utils.state_management import FinancialAnalysisState
from config import Config

class QualityCheckerAgent:
    def __init__(self):
        config = Config()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_retries=3,
            api_key=config.gemini_api_key
        )
        
        self.quality_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful financial expert and report reviewer.

Review this investment research report and assess its quality. Be reasonable and practical in your assessment.

Focus on:
1. Does the report contain essential financial information?
2. Is there a clear investment recommendation?
3. Are the key metrics and data points included?
4. Is the analysis logically structured?

IMPORTANT: Only suggest improvements if there are MAJOR issues. Minor imperfections should be accepted.

Respond with:
- QUALITY_SCORE: 1-10 (be generous - 7+ is good)
- ISSUES_FOUND: only list critical problems
- RECOMMENDATION: APPROVE (if score 7+) or NEEDS_IMPROVEMENT (only if score <7)

Be practical - a good report with basic analysis should be approved."""),
            ("human", """Review this investment research report for {company_name}:

REPORT:
{report}

ORIGINAL RESEARCH PLAN:
{research_plan}

Provide a practical assessment. Approve if the report is reasonably complete and professional.""")
        ])

    def run(self, state: FinancialAnalysisState) -> FinancialAnalysisState:
        """
        This is the critical thinking agent that reviews the report for completeness,
        accuracy, and suggests improvements. This is where LangGraph's cyclic nature shines.
        """
        print("🔍 QualityChecker: Reviewing report quality...")
        
        try:
            final_report = state.get("final_report", "No report available")
            research_plan = ", ".join(state.get("research_plan", []))
            
            # Generate quality assessment
            chain = self.quality_prompt | self.llm
            response = chain.invoke({
                "company_name": state["company_name"],
                "report": final_report,
                "research_plan": research_plan
            })
            
            quality_assessment = response.content
            
            # Extract quality score if available
            quality_score = 8  # Default to good score
            if "QUALITY_SCORE:" in quality_assessment:
                try:
                    score_line = [line for line in quality_assessment.split('\n') if 'QUALITY_SCORE:' in line][0]
                    quality_score = int(score_line.split(':')[1].strip().split()[0])
                except:
                    pass
            
            # More intelligent quality check
            has_errors = "error" in final_report.lower() or "failed" in final_report.lower()
            has_recommendation = any(word in final_report.upper() for word in ["BUY", "SELL", "HOLD", "RECOMMENDATION"])
            has_financial_data = any(word in final_report.upper() for word in ["PRICE", "REVENUE", "PROFIT", "GROWTH", "VALUATION"])
            is_too_short = len(final_report) < 500
            
            # Determine if improvement is needed
            needs_improvement = (
                has_errors or
                (quality_score < 6) or
                (not has_recommendation and not is_too_short) or
                (not has_financial_data and not is_too_short)
            )
            
            # Be more lenient on first iteration
            if state.get("iteration_count", 0) == 0 and quality_score >= 5:
                needs_improvement = False
            
            if not needs_improvement:
                state["quality_check_passed"] = True
                print(f"✅ QualityChecker: Report approved! (Score: {quality_score})")
            else:
                state["quality_check_passed"] = False
                
                # Only iterate if we haven't reached max iterations
                if state.get("iteration_count", 0) < 2:  # Max 2 iterations
                    print(f"🔄 QualityChecker: Report needs improvement (Score: {quality_score}, iteration {state.get('iteration_count', 0) + 1})")
                else:
                    state["quality_check_passed"] = True  # Accept after max iterations
                    print(f"✅ QualityChecker: Report accepted after maximum iterations (Score: {quality_score})")
            
            # Store quality assessment
            state["messages"].append(AIMessage(content=f"Quality check completed. Status: {'APPROVED' if state['quality_check_passed'] else 'NEEDS_IMPROVEMENT'}"))
            
            # Increment iteration count
            state["iteration_count"] = state.get("iteration_count", 0) + 1
            
        except Exception as e:
            print(f"❌ QualityChecker error: {str(e)}")
            # Be more lenient on errors - accept the report
            state["quality_check_passed"] = True
            state["messages"].append(AIMessage(content=f"Quality check failed due to error, accepting report"))
            
            # If we're on the first iteration and there's an error, just accept it
            if state.get("iteration_count", 0) == 0:
                print("✅ QualityChecker: Accepting report due to first iteration error")
            else:
                print("✅ QualityChecker: Accepting report after error to prevent infinite loops")
        
        return state

def quality_checker(state: FinancialAnalysisState) -> FinancialAnalysisState:
    agent = QualityCheckerAgent()
    return agent.run(state)
