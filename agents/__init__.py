"""
Autonomous Financial Analyst Agents

This package contains the 5 specialized agents that work together to analyze
companies and generate comprehensive financial reports.

Agents:
- QueryPlannerAgent: Breaks down analysis into actionable tasks
- DataFetcherAgent: Collects data from multiple financial APIs
- DataAnalystAgent: Performs sophisticated financial analysis
- ReportWriterAgent: Creates professional investment reports
- QualityCheckerAgent: Reviews and validates report quality
"""

from .query_planner import QueryPlannerAgent, query_planner
from .data_fetcher import DataFetcherAgent, data_fetcher
from .data_analyst import DataAnalystAgent, data_analyst
from .report_writer import ReportWriterAgent, report_writer
from .quality_checker import QualityCheckerAgent, quality_checker

__all__ = [
    'QueryPlannerAgent', 'query_planner',
    'DataFetcherAgent', 'data_fetcher', 
    'DataAnalystAgent', 'data_analyst',
    'ReportWriterAgent', 'report_writer',
    'QualityCheckerAgent', 'quality_checker'
]
