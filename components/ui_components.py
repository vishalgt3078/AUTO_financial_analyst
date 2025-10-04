"""
Streamlit UI Components for Autonomous Financial Analyst

This module contains all reusable UI components for the Streamlit application,
providing a clean and professional interface for the multi-agent financial analysis system.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

def render_main_header():
    """Render the main application header with branding"""
    st.markdown(
        """
        <div style="background: linear-gradient(90deg, #1f4e79 0%, #2e6da4 100%); 
                    padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">🤖 Autonomous Financial Analyst</h1>
            <p style="color: #e8f4f8; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
                Multi-Agent Financial Analysis System powered by LangGraph & Gemini AI
            </p>
            <p style="color: #b8d4e3; margin: 0.3rem 0 0 0; font-size: 1rem;">
                Professional-grade investment research with 5 specialized AI agents
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

def render_sidebar():
    """Render the sidebar with configuration and system info"""
    st.markdown("## ⚙️ Configuration")
    
    # API Configuration Section
    with st.expander("🔑 API Keys Setup", expanded=False):
        st.markdown("""
        **Required APIs (All Free!):**
        
        1. **🧠 Gemini API** - Google's AI for analysis
           - Get your free key: [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)
           - Free tier: 15 requests per minute
           
        2. **📈 Alpha Vantage API** - Financial data
           - Get your free key: [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
           - Free tier: 500 calls per day
           
        3. **📰 Stock News API** (Optional)
           - Get your free key: [Stock News API](https://stocknewsapi.com/)
           - Free tier: 100 calls per day
        
        **Setup Instructions:**
        - Add keys to `.env` file or Streamlit secrets
        - Restart the app after adding keys
        """)
    
    # Data Sources Section
    with st.expander("📊 Data Sources", expanded=False):
        st.markdown("""
        **Live Data Sources:**
        
        - 📊 **Yahoo Finance** - Stock prices, company info
        - 🏢 **SEC EDGAR** - Official financial filings
        - 📈 **Alpha Vantage** - Advanced financial metrics
        - 📰 **Stock News** - Recent financial news
        - 🌐 **Web Search** - Additional market insights
        """)
    
    # System Architecture
    st.markdown("## 🏗️ System Architecture")
    
    agents_info = {
        "🎯 QueryPlanner": "Breaks down analysis into actionable tasks",
        "🔍 DataFetcher": "Collects data from multiple APIs", 
        "📊 DataAnalyst": "Performs sophisticated financial analysis",
        "📝 ReportWriter": "Generates professional investment reports",
        "✅ QualityChecker": "Reviews and validates report quality"
    }
    
    for agent, description in agents_info.items():
        st.markdown(f"**{agent}**")
        st.caption(description)
        st.markdown("")

def render_analysis_form():
    """Render the main analysis input form"""
    st.markdown("### 🎯 Start Your Analysis")
    
    with st.form("analysis_form", clear_on_submit=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            company_symbol = st.text_input(
                "Enter Stock Symbol (e.g., AAPL, MSFT, TSLA, GOOGL)",
                placeholder="AAPL",
                help="Enter the stock ticker symbol for the company you want to analyze"
            ).upper().strip()
            
            # Analysis options
            st.markdown("**Analysis Options:**")
            col_opt1, col_opt2 = st.columns(2)
            
            with col_opt1:
                include_news = st.checkbox("📰 Include News Analysis", value=True)
                include_sec = st.checkbox("📋 Include SEC Filings", value=True)
            
            with col_opt2:
                include_sentiment = st.checkbox("💭 Sentiment Analysis", value=False, help="Experimental feature")
                detailed_report = st.checkbox("📄 Detailed Report", value=True)
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "🚀 Start Analysis", 
                type="primary",
                use_container_width=True
            )
        
        if submitted and company_symbol:
            # Store analysis options in session state
            st.session_state.analysis_options = {
                'include_news': include_news,
                'include_sec': include_sec,
                'include_sentiment': include_sentiment,
                'detailed_report': detailed_report
            }
            return company_symbol
    
    return None

def render_progress_tracker():
    """Render real-time progress tracking"""
    st.markdown("### 📊 Analysis Progress")
    
    # Get current progress from session state
    current_progress = st.session_state.get('analysis_progress', [])
    
    if not current_progress:
        # Default progress states
        progress_steps = [
            ("🎯 Planning", False),
            ("🔍 Data Collection", False),
            ("📊 Analysis", False),
            ("📝 Report Writing", False),
            ("✅ Quality Check", False)
        ]
    else:
        progress_steps = current_progress
    
    # Create a progress container
    with st.container():
        for i, (step, completed) in enumerate(progress_steps):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if completed:
                    st.success(f"{step} ✅")
                else:
                    st.info(f"{step} ⏳")
            
            with col2:
                if completed:
                    st.markdown("**100%**")
                else:
                    st.markdown("**0%**")
    
    # Add a progress bar
    if st.session_state.get('analysis_in_progress', False):
        progress_value = st.session_state.get('progress_value', 0)
        st.progress(progress_value / 100)
        
        # Show current status
        current_status = st.session_state.get('current_status', 'Initializing...')
        st.info(f"🔄 {current_status}")

def render_system_status():
    """Render system status indicators"""
    st.markdown("### 🔧 System Status")
    
    # Check API configurations
    from config import Config
    config = Config()
    
    # Gemini API Status
    if config.gemini_api_key:
        st.success("🧠 Gemini AI: Ready")
    else:
        st.error("🧠 Gemini AI: Not configured")
    
    # Alpha Vantage API Status
    if config.alpha_vantage_api_key:
        st.success("📈 Alpha Vantage: Ready")
    else:
        st.error("📈 Alpha Vantage: Not configured")
    
    # Stock News API Status (Optional)
    if hasattr(config, 'stock_news_api_key') and config.stock_news_api_key:
        st.success("📰 Stock News: Ready")
    else:
        st.warning("📰 Stock News: Optional")
    
    # System metrics
    with st.expander("📊 System Metrics"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Analyses Today", st.session_state.get('analyses_today', 0))
        with col2:
            st.metric("Success Rate", f"{st.session_state.get('success_rate', 95)}%")

def render_results(results: Dict[str, Any]):
    """Render comprehensive analysis results"""
    if "error" in results:
        st.error(f"❌ Analysis Error: {results['error']}")
        return
    
    # Success header
    st.markdown(
        """
        <div style="background: linear-gradient(90deg, #28a745 0%, #20c997 100%); 
                    padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <h3 style="color: white; margin: 0;">✅ Analysis Complete!</h3>
            <p style="color: #d4edda; margin: 0.5rem 0 0 0;">
                Professional investment research report generated successfully
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Summary", 
        "📈 Financial Data", 
        "🔍 Detailed Analysis", 
        "📄 Full Report",
        "⚙️ Technical Details"
    ])
    
    with tab1:
        render_executive_summary(results)
    
    with tab2:
        render_financial_data(results)
    
    with tab3:
        render_detailed_analysis(results)
    
    with tab4:
        render_full_report(results)
    
    with tab5:
        render_technical_details(results)

def render_executive_summary(results: Dict[str, Any]):
    """Render executive summary with key metrics"""
    st.markdown("### 📊 Executive Summary")
    
    # Extract key information from results
    raw_data = results.get('raw_data', {})
    stock_data = raw_data.get('stock_data', {})
    
    if stock_data and 'error' not in stock_data:
        info = stock_data.get('company_info', {})
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_price = info.get('currentPrice', 'N/A')
            st.metric("Current Price", f"${current_price}" if isinstance(current_price, (int, float)) else current_price)
        
        with col2:
            market_cap = info.get('marketCap', 'N/A')
            if isinstance(market_cap, (int, float)):
                market_cap_str = f"${market_cap/1e9:.1f}B" if market_cap > 1e9 else f"${market_cap/1e6:.1f}M"
            else:
                market_cap_str = str(market_cap)
            st.metric("Market Cap", market_cap_str)
        
        with col3:
            pe_ratio = info.get('trailingPE', 'N/A')
            st.metric("P/E Ratio", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio)
        
        with col4:
            dividend_yield = info.get('dividendYield', 'N/A')
            if isinstance(dividend_yield, (int, float)):
                dividend_str = f"{dividend_yield*100:.2f}%"
            else:
                dividend_str = str(dividend_yield)
            st.metric("Dividend Yield", dividend_str)
        
        # Company info
        st.markdown("### 🏢 Company Information")
        
        company_info_cols = st.columns(2)
        with company_info_cols[0]:
            st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
            st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
            st.markdown(f"**Country:** {info.get('country', 'N/A')}")
        
        with company_info_cols[1]:
            st.markdown(f"**Employees:** {info.get('fullTimeEmployees', 'N/A'):,}" if isinstance(info.get('fullTimeEmployees'), (int, float)) else f"**Employees:** {info.get('fullTimeEmployees', 'N/A')}")
            st.markdown(f"**Exchange:** {info.get('exchange', 'N/A')}")
            st.markdown(f"**Currency:** {info.get('currency', 'N/A')}")
        
        # Business summary
        if 'longBusinessSummary' in info:
            st.markdown("### 📋 Business Summary")
            st.write(info['longBusinessSummary'][:500] + "..." if len(info['longBusinessSummary']) > 500 else info['longBusinessSummary'])
    
    else:
        st.warning("Stock data not available for detailed summary")

def render_financial_data(results: Dict[str, Any]):
    """Render financial data with charts"""
    st.markdown("### 📈 Financial Data Visualization")
    
    raw_data = results.get('raw_data', {})
    stock_data = raw_data.get('stock_data', {})
    
    if stock_data and 'error' not in stock_data:
        price_history = stock_data.get('price_history')
        
        if price_history is not None and not price_history.empty:
            # Stock price chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=price_history.index,
                y=price_history['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='#2e6da4', width=2)
            ))
            
            fig.update_layout(
                title=f"Stock Price History - {results.get('company_name', 'Unknown')}",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                hovermode='x unified',
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart
            if 'Volume' in price_history.columns:
                fig_volume = go.Figure()
                fig_volume.add_trace(go.Bar(
                    x=price_history.index,
                    y=price_history['Volume'],
                    name='Volume',
                    marker_color='rgba(46, 109, 164, 0.6)'
                ))
                
                fig_volume.update_layout(
                    title="Trading Volume",
                    xaxis_title="Date",
                    yaxis_title="Volume",
                    showlegend=False
                )
                
                st.plotly_chart(fig_volume, use_container_width=True)
        
        # Financial statements summary
        financials = stock_data.get('financials')
        if financials is not None and not financials.empty:
            st.markdown("### 💰 Financial Statements (Recent)")
            
            # Display recent financial data
            recent_financials = financials.iloc[:, :4]  # Last 4 periods
            st.dataframe(recent_financials.head(10), use_container_width=True)
    
    else:
        st.warning("Financial data not available for visualization")

def render_detailed_analysis(results: Dict[str, Any]):
    """Render detailed analysis results"""
    st.markdown("### 🔍 Detailed Financial Analysis")
    
    analyzed_data = results.get('analyzed_data', {})
    
    if 'detailed_analysis' in analyzed_data:
        analysis_content = analyzed_data['detailed_analysis']
        
        # Split analysis into sections if possible
        sections = analysis_content.split('\n\n')
        
        for i, section in enumerate(sections):
            if section.strip():
                # Try to identify section headers
                if section.strip().isupper() or section.startswith('#'):
                    st.markdown(f"#### {section.strip()}")
                else:
                    st.markdown(section.strip())
                    
                if i < len(sections) - 1:
                    st.markdown("---")
    
    else:
        st.warning("Detailed analysis not available")

def render_full_report(results: Dict[str, Any]):
    """Render the complete investment report"""
    st.markdown("### 📄 Complete Investment Research Report")
    
    final_report = results.get('final_report', '')
    
    if final_report:
        # Add download button
        st.download_button(
            label="📥 Download Report",
            data=final_report,
            file_name=f"investment_report_{results.get('company_name', 'analysis')}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
        
        # Display report with better formatting
        st.markdown("---")
        
        # Convert the report to markdown format
        formatted_report = final_report.replace('\n\n', '\n\n---\n\n')
        st.markdown(formatted_report)
    
    else:
        st.warning("Full report not available")

def render_technical_details(results: Dict[str, Any]):
    """Render technical details and metadata"""
    st.markdown("### ⚙️ Technical Analysis Details")
    
    # Analysis metadata
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Analysis Metadata")
        analyzed_data = results.get('analyzed_data', {})
        if 'timestamp' in analyzed_data:
            st.write(f"**Analysis Time:** {analyzed_data['timestamp']}")
        if 'data_sources_used' in analyzed_data:
            st.write(f"**Data Sources:** {', '.join(analyzed_data['data_sources_used'])}")
        
        iteration_count = results.get('iteration_count', 0)
        st.write(f"**Quality Iterations:** {iteration_count}")
        
        quality_passed = results.get('quality_check_passed', False)
        st.write(f"**Quality Check:** {'✅ Passed' if quality_passed else '❌ Failed'}")
    
    with col2:
        st.markdown("#### 🔧 System Performance")
        st.write("**Agent Performance:**")
        
        messages = results.get('messages', [])
        if messages:
            for message in messages[-5:]:  # Last 5 messages
                st.caption(f"• {message.content if hasattr(message, 'content') else str(message)}")
    
    # Raw data inspection
    with st.expander("🔍 Raw Data Inspection"):
        raw_data = results.get('raw_data', {})
        
        for source, data in raw_data.items():
            st.markdown(f"**{source.title()} Data:**")
            
            if isinstance(data, dict):
                if 'error' in data:
                    st.error(f"Error: {data['error']}")
                else:
                    # Show structure
                    st.json({k: f"{type(v).__name__} - {len(str(v))} chars" for k, v in list(data.items())[:10]})
            else:
                st.write(f"Data type: {type(data).__name__}")
            
            st.markdown("---")

def display_raw_data(raw_data: Dict[str, Any]):
    """Display raw data in organized format"""
    st.markdown("### 📊 Raw Data Sources")
    
    for source, data in raw_data.items():
        with st.expander(f"📁 {source.replace('_', ' ').title()}"):
            if isinstance(data, dict) and 'error' not in data:
                if source == 'stock_data':
                    display_stock_data_details(data)
                elif source == 'sec_filings':
                    display_sec_filings_details(data)
                else:
                    st.json(data)
            else:
                st.error(f"Error loading {source}: {data.get('error', 'Unknown error')}")

def display_stock_data_details(stock_data: Dict[str, Any]):
    """Display detailed stock data"""
    info = stock_data.get('company_info', {})
    
    # Key metrics table
    if info:
        metrics_df = pd.DataFrame([
            ['Current Price', info.get('currentPrice', 'N/A')],
            ['Market Cap', info.get('marketCap', 'N/A')],
            ['P/E Ratio', info.get('trailingPE', 'N/A')],
            ['Revenue Growth', info.get('revenueGrowth', 'N/A')],
            ['Profit Margins', info.get('profitMargins', 'N/A')]
        ], columns=['Metric', 'Value'])
        
        st.dataframe(metrics_df, use_container_width=True)

def display_sec_filings_details(sec_data: Dict[str, Any]):
    """Display SEC filings data"""
    if 'recent_filings' in sec_data:
        filings = sec_data['recent_filings']
        if filings:
            filings_df = pd.DataFrame(filings)
            st.dataframe(filings_df, use_container_width=True)
        else:
            st.info("No recent filings found")
    else:
        st.json(sec_data)

def display_metadata(results: Dict[str, Any]):
    """Display analysis metadata"""
    st.markdown("### ⚙️ Analysis Metadata")
    
    metadata = {
        'Company': results.get('company_name', 'N/A'),
        'Analysis Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Data Sources': len(results.get('raw_data', {})),
        'Quality Iterations': results.get('iteration_count', 0),
        'Quality Check Passed': results.get('quality_check_passed', False)
    }
    
    for key, value in metadata.items():
        st.write(f"**{key}:** {value}")

def render_dashboard():
    """Main dashboard function that renders the complete UI"""
    # Render the main header
    render_main_header()
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Main analysis form
        company_symbol = render_analysis_form()
        
        # Trigger analysis if form was submitted
        if company_symbol and company_symbol not in st.session_state.get('processed_symbols', []):
            trigger_analysis(company_symbol)
        
        # Show progress if analysis is running
        if st.session_state.get('analysis_in_progress', False):
            render_progress_tracker()
        
        # Show results if available
        if 'analysis_results' in st.session_state:
            render_results(st.session_state['analysis_results'])
    
    with col2:
        # Sidebar with configuration and status
        render_sidebar()
        render_system_status()

def trigger_analysis(company_symbol):
    """Trigger the financial analysis workflow"""
    import time
    from utils.helpers import run_financial_analysis
    
    # Initialize session state
    if 'processed_symbols' not in st.session_state:
        st.session_state.processed_symbols = []
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    if 'analysis_in_progress' not in st.session_state:
        st.session_state.analysis_in_progress = False
    
    # Start analysis
    st.session_state.analysis_in_progress = True
    st.session_state.processed_symbols.append(company_symbol)
    
    # Create progress container
    progress_container = st.container()
    
    with progress_container:
        st.info(f"🚀 Starting analysis for {company_symbol}...")
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(message, progress):
            progress_bar.progress(progress / 100)
            status_text.text(f"📊 {message}")
            time.sleep(0.5)  # Small delay for visual effect
        
        try:
            # Check if API keys are configured
            from config import Config
            config = Config()
            
            if not config.is_configured():
                # Demo mode - show sample analysis
                status_text.text("🎯 Planning analysis...")
                progress_bar.progress(10)
                time.sleep(1)
                
                status_text.text("🔍 Collecting data...")
                progress_bar.progress(30)
                time.sleep(1)
                
                status_text.text("📊 Analyzing data...")
                progress_bar.progress(60)
                time.sleep(1)
                
                status_text.text("📝 Writing report...")
                progress_bar.progress(80)
                time.sleep(1)
                
                # Create demo results
                result = create_demo_analysis(company_symbol)
                
                status_text.text("✅ Analysis complete!")
                progress_bar.progress(100)
                
                # Store results
                st.session_state.analysis_results = result
                st.session_state.analysis_in_progress = False
                
                # Show success message
                st.success(f"🎉 Demo analysis completed for {company_symbol}!")
                st.warning("⚠️ This is a demo analysis. Configure API keys for real data.")
                
                # Auto-refresh to show results
                st.rerun()
            else:
                # Real analysis with API keys
                status_text.text("🎯 Planning analysis...")
                progress_bar.progress(10)
                time.sleep(1)
                
                status_text.text("🔍 Collecting data...")
                progress_bar.progress(30)
                time.sleep(1)
                
                status_text.text("📊 Analyzing data...")
                progress_bar.progress(60)
                time.sleep(1)
                
                status_text.text("📝 Writing report...")
                progress_bar.progress(80)
                time.sleep(1)
                
                # Run the actual analysis
                result = run_financial_analysis(company_symbol, progress_callback)
                
                status_text.text("✅ Analysis complete!")
                progress_bar.progress(100)
                
                # Store results
                st.session_state.analysis_results = result
                st.session_state.analysis_in_progress = False
                
                # Show success message
                st.success(f"🎉 Analysis completed for {company_symbol}!")
                
                # Auto-refresh to show results
                st.rerun()
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            st.session_state.analysis_in_progress = False
            st.session_state.analysis_results = {
                'error': str(e),
                'company_name': company_symbol
            }

def create_demo_analysis(company_symbol):
    """Create a demo analysis for testing without API keys"""
    from datetime import datetime
    
    # Get current date and time
    current_date = datetime.now()
    formatted_date = current_date.strftime('%B %d, %Y')
    iso_timestamp = current_date.isoformat()
    
    # Check if it's an Indian stock (common Indian stock symbols)
    indian_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'WIPRO', 'ITC', 'ICICIBANK', 'SBIN', 'MARUTI', 'TATAMOTORS']
    is_indian = any(stock in company_symbol.upper() for stock in indian_stocks)
    
    if is_indian:
        # Indian stock demo data
        currency = '₹'
        market = 'Indian Market'
        exchange = 'NSE'
        country = 'India'
        price = 1500.25
        market_cap = 2500000000000  # 2.5T in INR
        market_cap_str = f"₹{market_cap/1e12:.1f}T"
        sector = 'Technology'
        industry = 'Information Technology Services'
        business_summary = f"{company_symbol} is a leading Indian technology company with strong market position and innovative products in the Indian market."
    else:
        # International stock demo data
        currency = '$'
        market = 'International Market'
        exchange = 'NASDAQ'
        country = 'United States'
        price = 150.25
        market_cap = 2500000000000  # 2.5T in USD
        market_cap_str = f"${market_cap/1e12:.1f}T"
        sector = 'Technology'
        industry = 'Software'
        business_summary = f"{company_symbol} is a leading technology company with strong market position and innovative products."
    
    return {
        'company_name': company_symbol,
        'raw_data': {
            'stock_data': {
                'company_info': {
                    'currentPrice': price,
                    'marketCap': market_cap,
                    'trailingPE': 25.5,
                    'dividendYield': 0.02,
                    'sector': sector,
                    'industry': industry,
                    'country': country,
                    'fullTimeEmployees': 150000,
                    'exchange': exchange,
                    'currency': currency,
                    'longBusinessSummary': business_summary
                },
                'price_history': None,  # Would be a pandas DataFrame in real analysis
                'market': market,
                'currency': currency
            }
        },
        'analyzed_data': {
            'detailed_analysis': f"""
# Financial Analysis for {company_symbol}

## Executive Summary
{company_symbol} shows strong financial performance with solid growth prospects. The company demonstrates robust fundamentals and market leadership in its sector.

## Key Metrics
- Current Price: {currency}{price}
- Market Cap: {market_cap_str}
- P/E Ratio: 25.5
- Dividend Yield: 2.0%
- Market: {market}

## Investment Recommendation
**BUY** - Strong fundamentals and growth potential

## Risk Factors
- Market volatility
- Competitive pressures
- Regulatory changes

*This is a demo analysis. Configure API keys for real-time data.*
            """,
            'timestamp': iso_timestamp,
            'data_sources_used': ['demo_data']
        },
        'final_report': f"""
# Investment Research Report: {company_symbol}

**Date: {formatted_date}**

## Executive Summary
{company_symbol} demonstrates strong financial health with excellent growth prospects. The company's innovative approach and market leadership position it well for future success.

## Investment Recommendation: BUY
Target Price: {currency}{price * 1.2:.2f}

## Financial Analysis
The company shows robust fundamentals with a healthy P/E ratio and strong market position. Revenue growth has been consistent, and the company maintains a strong balance sheet.

## Risk Assessment
While the company shows strong fundamentals, investors should be aware of market volatility and competitive pressures in the technology sector.

## Conclusion
{company_symbol} presents an attractive investment opportunity for long-term growth investors.

*This is a demo analysis. Configure API keys for real-time data and comprehensive analysis.*
*Generated on {formatted_date}*
        """,
        'iteration_count': 1,
        'quality_check_passed': True,
        'messages': [
            f"Demo analysis completed for {company_symbol}",
            "This is a sample analysis for demonstration purposes"
        ]
    }
