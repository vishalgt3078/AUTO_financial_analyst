from langgraph.graph import StateGraph, END, START
from utils.state_management import FinancialAnalysisState
from agents.query_planner import query_planner
from agents.data_fetcher import data_fetcher
from agents.data_analyst import data_analyst
from agents.report_writer import report_writer
from agents.quality_checker import quality_checker

def create_analysis_graph():
    workflow = StateGraph(FinancialAnalysisState)
    
    # Add agents
    workflow.add_node("query_planner", query_planner)
    workflow.add_node("data_fetcher", data_fetcher)
    workflow.add_node("data_analyst", data_analyst)
    workflow.add_node("report_writer", report_writer)
    workflow.add_node("quality_checker", quality_checker)
    
    # Add edges
    workflow.add_edge(START, "query_planner")
    workflow.add_edge("query_planner", "data_fetcher")
    workflow.add_edge("data_fetcher", "data_analyst")
    workflow.add_edge("data_analyst", "report_writer")
    workflow.add_edge("report_writer", "quality_checker")
    
    # Conditional edges - improved logic
    def should_continue(state):
        """Determine if we should continue or end the workflow"""
        quality_passed = state.get("quality_check_passed", False)
        iteration_count = state.get("iteration_count", 0)
        
        # End if quality check passed or if we've reached max iterations
        if quality_passed or iteration_count >= 2:
            return "end"
        else:
            return "data_fetcher"
    
    workflow.add_conditional_edges(
        "quality_checker",
        should_continue,
        {"data_fetcher": "data_fetcher", "end": END}
    )
    
    return workflow.compile()

def run_financial_analysis(company_name: str, progress_callback=None):
    graph = create_analysis_graph()
    
    initial_state = FinancialAnalysisState(
        company_name=company_name,
        research_plan=[],
        raw_data={},
        analyzed_data={},
        final_report="",
        messages=[],
        iteration_count=0,
        quality_check_passed=False
    )
    
    if progress_callback:
        progress_callback("Initializing analysis", 20)
    
    result = graph.invoke(initial_state)
    
    if progress_callback:
        progress_callback("Analysis complete", 100)
    
    return result

def format_currency(value, currency='USD'):
    """Format a numeric value as currency"""
    if value is None or value == 'N/A':
        return 'N/A'
    try:
        if isinstance(value, str):
            value = float(value.replace('$', '').replace(',', ''))
        return f"${value:,.2f}"
    except (ValueError, TypeError):
        return str(value)

def format_percentage(value, decimals=2):
    """Format a numeric value as percentage"""
    if value is None or value == 'N/A':
        return 'N/A'
    try:
        if isinstance(value, str):
            value = float(value.replace('%', ''))
        return f"{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)

def safe_float_conversion(value, default=0.0):
    """Safely convert a value to float"""
    if value is None or value == 'N/A':
        return default
    try:
        if isinstance(value, str):
            value = value.replace('$', '').replace(',', '').replace('%', '')
        return float(value)
    except (ValueError, TypeError):
        return default

def extract_company_symbol(company_input):
    """Extract company symbol from various input formats"""
    if not company_input:
        return None
    
    # Clean the input
    symbol = str(company_input).upper().strip()
    
    # Remove common prefixes/suffixes
    symbol = symbol.replace('STOCK:', '').replace('TICKER:', '').replace('SYMBOL:', '')
    
    # Basic validation - should be 1-5 uppercase letters
    if symbol.isalpha() and 1 <= len(symbol) <= 5:
        return symbol
    
    return None
