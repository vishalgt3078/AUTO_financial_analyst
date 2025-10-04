"""
Data Source Management Utilities

This module provides utilities for managing various financial data sources
and APIs used by the autonomous financial analyst system.
"""

import os
import requests
from typing import Dict, Any, Optional
import yfinance as yf
from datetime import datetime, timedelta

class DataSourceManager:
    """Centralized manager for all data sources"""
    
    def __init__(self):
        self.api_limits = {
            'alpha_vantage': {'daily_limit': 500, 'calls_today': 0},
            'stock_news': {'daily_limit': 100, 'calls_today': 0},
            'sec_edgar': {'rate_limit': '10_per_second', 'calls_today': 0}
        }
    
    def check_api_status(self, api_name: str) -> Dict[str, Any]:
        """Check the status of a specific API"""
        if api_name in self.api_limits:
            limit_info = self.api_limits[api_name]
            return {
                'available': limit_info['calls_today'] < limit_info.get('daily_limit', float('inf')),
                'remaining_calls': limit_info.get('daily_limit', 0) - limit_info['calls_today'],
                'calls_used': limit_info['calls_today']
            }
        return {'available': True, 'remaining_calls': 'unlimited', 'calls_used': 0}
    
    def increment_api_usage(self, api_name: str, calls: int = 1):
        """Increment API usage counter"""
        if api_name in self.api_limits:
            self.api_limits[api_name]['calls_today'] += calls
    
    def reset_daily_counters(self):
        """Reset all daily API counters (call this daily)"""
        for api_info in self.api_limits.values():
            api_info['calls_today'] = 0

class APIValidator:
    """Validates API keys and connections"""
    
    @staticmethod
    def validate_gemini_api(api_key: str) -> bool:
        """Validate Gemini API key"""
        try:
            if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
                return False
            # Basic format validation
            return len(api_key) > 20 and api_key.startswith('AI')
        except Exception:
            return False
    
    @staticmethod
    def validate_alpha_vantage_api(api_key: str) -> bool:
        """Validate Alpha Vantage API key"""
        try:
            if not api_key or api_key == "YOUR_ALPHA_VANTAGE_API_KEY_HERE":
                return False
            
            # Test with a simple API call
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return "Error Message" not in data
            return False
        except Exception:
            return False
    
    @staticmethod
    def validate_yahoo_finance() -> bool:
        """Validate Yahoo Finance access (no API key required)"""
        try:
            ticker = yf.Ticker("AAPL")
            info = ticker.info
            return bool(info and 'symbol' in info)
        except Exception:
            return False

class DataQualityChecker:
    """Checks data quality and completeness"""
    
    @staticmethod
    def check_stock_data_quality(stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check quality of stock data"""
        quality_score = 0
        issues = []
        
        if 'company_info' in stock_data:
            info = stock_data['company_info']
            
            # Check essential fields
            essential_fields = ['currentPrice', 'marketCap', 'symbol']
            for field in essential_fields:
                if field in info and info[field] is not None:
                    quality_score += 20
                else:
                    issues.append(f"Missing {field}")
            
            # Check optional but important fields
            optional_fields = ['trailingPE', 'forwardPE', 'dividendYield', 'sector', 'industry']
            for field in optional_fields:
                if field in info and info[field] is not None:
                    quality_score += 8
        else:
            issues.append("Missing company info")
        
        if 'price_history' in stock_data:
            price_history = stock_data['price_history']
            if not price_history.empty:
                quality_score += 20
            else:
                issues.append("Empty price history")
        else:
            issues.append("Missing price history")
        
        return {
            'quality_score': min(quality_score, 100),
            'issues': issues,
            'status': 'good' if quality_score >= 80 else 'fair' if quality_score >= 60 else 'poor'
        }
    
    @staticmethod
    def check_analysis_completeness(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check completeness of analysis"""
        required_sections = [
            'financial_health', 'growth_prospects', 'valuation',
            'risk_factors', 'recommendation'
        ]
        
        content = analysis_data.get('detailed_analysis', '').lower()
        found_sections = []
        
        for section in required_sections:
            if section.replace('_', ' ') in content:
                found_sections.append(section)
        
        completeness_score = (len(found_sections) / len(required_sections)) * 100
        
        return {
            'completeness_score': completeness_score,
            'found_sections': found_sections,
            'missing_sections': list(set(required_sections) - set(found_sections)),
            'status': 'complete' if completeness_score >= 80 else 'partial' if completeness_score >= 60 else 'incomplete'
        }

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self):
        self.call_history = {}
    
    def can_make_call(self, api_name: str, max_calls_per_minute: int = 60) -> bool:
        """Check if we can make an API call without exceeding rate limits"""
        now = datetime.now()
        
        if api_name not in self.call_history:
            self.call_history[api_name] = []
        
        # Remove calls older than 1 minute
        self.call_history[api_name] = [
            call_time for call_time in self.call_history[api_name]
            if now - call_time < timedelta(minutes=1)
        ]
        
        return len(self.call_history[api_name]) < max_calls_per_minute
    
    def record_call(self, api_name: str):
        """Record that an API call was made"""
        if api_name not in self.call_history:
            self.call_history[api_name] = []
        
        self.call_history[api_name].append(datetime.now())

# Global instances
data_source_manager = DataSourceManager()
api_validator = APIValidator()
data_quality_checker = DataQualityChecker()
rate_limiter = RateLimiter()
