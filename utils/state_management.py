from typing import Dict, List, Optional, Any, TypedDict, Annotated
from dataclasses import dataclass
from langgraph.graph.message import add_messages

class FinancialAnalysisState(TypedDict):
    company_name: str
    research_plan: List[str]
    raw_data: Dict[str, Any]
    analyzed_data: Dict[str, Any]
    final_report: str
    messages: Annotated[List[Any], add_messages]
    iteration_count: int
    quality_check_passed: bool

@dataclass
class ResearchTask:
    task_type: str
    description: str
    priority: int
    completed: bool = False
