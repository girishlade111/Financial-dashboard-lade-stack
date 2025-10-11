import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="Tech Company Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load mock data function
@st.cache_data
def load_mock_data():
    """Load mock financial data for 2024 and 2025"""
    data_2024 = {
        'Quarter': ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024'],
        'Year': [2024, 2024, 2024, 2024],
        'Revenue': [95000000, 108000000, 122000000, 138000000],
        'Operating_Expenses': [68000000, 75000000, 84000000, 92000000],
        'Marketing_Expenses': [12000000, 14000000, 16000000, 18000000],
        'R&D_Expenses': [18000000, 20000000, 23000000, 26000000],
        'Administrative_Expenses': [10000000, 11000000, 12000000, 13000000],
        'Net_Profit': [27000000, 33000000, 38000000, 46000000],
        'Gross_Margin': [0.72, 0.69, 0.66, 0.63],
        'Operating_Margin': [0.28, 0.31, 0.34, 0.36],
        'Monthly_Active_Users': [10000000, 12000000, 14000000, 16000000],
        'Employee_Count': [1800, 2000, 2200, 2400]
    }
    data_2025 = {
        'Quarter': ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025'],
        'Year': [2025, 2025, 2025, 2025],
        'Revenue': [125000000, 142000000, 168000000, 195000000],
        'Operating_Expenses': [85000000, 92000000, 105000000, 118000000],
        'Marketing_Expenses': [15000000, 18000000, 22000000, 25000000],
        'R&D_Expenses': [25000000, 28000000, 32000000, 38000000],
        'Administrative_Expenses': [12000000, 13000000, 15000000, 17000000],
        'Net_Profit': [40000000, 50000000, 63000000, 77000000],
        'Gross_Margin': [0.68, 0.65, 0.62, 0.60],
        'Operating_Margin': [0.32, 0.35, 0.38, 0.40],
        'Monthly_Active_Users': [15000000, 18500000, 22000000, 26500000],
        'Employee_Count': [2500, 2750, 3100, 3450]
    }
    df_2024 = pd.DataFrame(data_2024)
    df_2025 = pd.DataFrame(data_2025)
    return pd.concat([df_2024, df_2025], ignore_index=True)

# Load data function with CSV upload support
@st.cache_data
def load_data(uploaded_file=None):
    """Load data from uploaded CSV or use mock data"""
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            return df
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")
            return load_mock_data()
    else:
        return load_mock_data()

# Calculate key metrics
def calculate_metrics(df):
    """Calculate key financial metrics"""
    total_revenue = df['Revenue'].sum()
    total_profit = df['Net_Profit'].sum()
    avg_margin = df['Operating_Margin'].mean()
    
    # Calculate growth rate (Q4 vs Q1)
    if len(df) >= 4:
        q1_revenue = df['Revenue'].iloc[0]
        q4_revenue = df['Revenue'].iloc[-1]
        growth_rate = ((q4_revenue - q1_revenue) / q1_revenue) * 100
    else:
        growth_rate = 0
    
    return {
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'avg_margin': avg_margin,
        'growth_rate': growth_rate
    }

# Sidebar with contact information and filters
def render_sidebar(df):
    """Render sidebar with contact information, file upload, and filters"""
    st.sidebar.markdown("## 📊 Financial Dashboard")
    st.sidebar.markdown("---")
    
    # File upload
    st.sidebar.markdown("### Upload CSV Data")
    
    # Multi-company comparison mode
    multi_company_mode = st.sidebar.checkbox("📊 Multi-Company Comparison", value=False,
                                              help="Compare multiple companies side-by-side")
    
    if multi_company_mode:
        uploaded_files = st.sidebar.file_uploader(
            "Upload Company Data Files",
            type="csv",
            accept_multiple_files=True,
            help="Upload multiple CSV files to compare companies"
        )
        
        # Company names input
        if uploaded_files:
            st.sidebar.markdown("**Company Names:**")
            company_names = []
            for i, file in enumerate(uploaded_files):
                default_name = file.name.replace('.csv', '')
                company_name = st.sidebar.text_input(
                    f"Company {i+1} Name",
                    value=default_name,
                    key=f"company_name_{i}"
                )
                company_names.append(company_name)
        else:
            company_names = []
        
        uploaded_file = None
    else:
        uploaded_file = st.sidebar.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload your financial data CSV to replace mock data"
        )
        uploaded_files = []
        company_names = []
    
    st.sidebar.markdown("---")
    
    # Data filters
    st.sidebar.markdown("### 🔍 Data Filters")
    
    # Year-over-Year comparison toggle
    show_yoy = st.sidebar.checkbox("📊 Year-over-Year Comparison", value=False, 
                                    help="Compare 2024 vs 2025 performance")
    
    # Predictive analytics toggle
    show_forecast = st.sidebar.checkbox("🔮 Revenue Forecast", value=False,
                                         help="Show predictive revenue forecast for next quarters")
    
    # Quarter/Date range filter
    if 'Quarter' in df.columns:
        quarters = df['Quarter'].tolist()
        selected_quarters = st.sidebar.multiselect(
            "Select Quarters",
            options=quarters,
            default=quarters,
            help="Filter data by specific quarters"
        )
    else:
        selected_quarters = []
    
    # Financial category filter
    st.sidebar.markdown("**Financial Categories**")
    show_revenue = st.sidebar.checkbox("Revenue & Profit", value=True)
    show_expenses = st.sidebar.checkbox("Expenses", value=True)
    show_margins = st.sidebar.checkbox("Margins", value=True)
    show_business = st.sidebar.checkbox("Business Metrics", value=True)
    
    st.sidebar.markdown("---")
    
    # Contact information
    st.sidebar.markdown("### 📞 Contact Information")
    st.sidebar.markdown("**Girish Lade**")
    st.sidebar.markdown("📧 [girish@ladestack.in](mailto:girish@ladestack.in)")
    st.sidebar.markdown("📱 [Instagram: @girish_lade_](https://instagram.com/girish_lade_)")
    st.sidebar.markdown("💻 [GitHub: girishlade111](https://github.com/girishlade111)")
    st.sidebar.markdown("🌐 [Visit LadeStack.in](https://ladestack.in)")
    
    filters = {
        'uploaded_file': uploaded_file,
        'selected_quarters': selected_quarters,
        'show_revenue': show_revenue,
        'show_expenses': show_expenses,
        'show_margins': show_margins,
        'show_business': show_business,
        'show_yoy': show_yoy,
        'show_forecast': show_forecast,
        'multi_company_mode': multi_company_mode,
        'uploaded_files': uploaded_files,
        'company_names': company_names
    }
    
    return filters

# Main dashboard content
def render_dashboard(df, filters):
    """Render main dashboard content"""
    
    # Title and description
    if filters['multi_company_mode'] and filters['uploaded_files']:
        st.title("🏢 Multi-Company Financial Comparison Dashboard")
        st.markdown("Comparative analysis of multiple companies' financial performance")
    else:
        st.title("🚀 Tech Company Financial Dashboard 2025")
        st.markdown("Interactive financial analytics and performance metrics")
    
    # Multi-Company Comparison Mode
    if filters['multi_company_mode'] and filters['uploaded_files']:
        # Load all company data
        company_datasets = []
        for i, file in enumerate(filters['uploaded_files']):
            try:
                df_company = pd.read_csv(file)
                company_name = filters['company_names'][i] if i < len(filters['company_names']) else f"Company {i+1}"
                company_datasets.append({
                    'name': company_name,
                    'data': df_company
                })
            except Exception as e:
                st.error(f"Error loading {file.name}: {e}")
        
        if len(company_datasets) >= 2:
            st.markdown("---")
            
            # Compare revenue across companies
            st.subheader("📊 Revenue Comparison Across Companies")
            
            fig_multi_revenue = go.Figure()
            
            for company in company_datasets:
                df_comp = company['data']
                if 'Quarter' in df_comp.columns and 'Revenue' in df_comp.columns:
                    # Get 2025 data if Year column exists
                    if 'Year' in df_comp.columns:
                        df_comp = df_comp[df_comp['Year'] == 2025]
                    
                    fig_multi_revenue.add_trace(go.Bar(
                        name=company['name'],
                        x=df_comp['Quarter'].tolist(),
                        y=df_comp['Revenue'].tolist(),
                        text=[f"${v/1000000:.1f}M" for v in df_comp['Revenue'].tolist()],
                        textposition='auto'
                    ))
            
            fig_multi_revenue.update_layout(
                title='Quarterly Revenue Comparison',
                xaxis_title='Quarter',
                yaxis_title='Revenue ($)',
                barmode='group',
                height=500
            )
            
            st.plotly_chart(fig_multi_revenue, use_container_width=True)
            
            # Compare key metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💰 Total Revenue Comparison")
                
                revenue_comparison = []
                for company in company_datasets:
                    df_comp = company['data']
                    if 'Revenue' in df_comp.columns:
                        if 'Year' in df_comp.columns:
                            df_comp = df_comp[df_comp['Year'] == 2025]
                        total_rev = df_comp['Revenue'].sum()
                        revenue_comparison.append({
                            'Company': company['name'],
                            'Total Revenue': f"${total_rev:,.0f}"
                        })
                
                st.dataframe(pd.DataFrame(revenue_comparison), use_container_width=True)
            
            with col2:
                st.subheader("💵 Net Profit Comparison")
                
                profit_comparison = []
                for company in company_datasets:
                    df_comp = company['data']
                    if 'Net_Profit' in df_comp.columns:
                        if 'Year' in df_comp.columns:
                            df_comp = df_comp[df_comp['Year'] == 2025]
                        total_profit = df_comp['Net_Profit'].sum()
                        profit_comparison.append({
                            'Company': company['name'],
                            'Total Net Profit': f"${total_profit:,.0f}"
                        })
                
                st.dataframe(pd.DataFrame(profit_comparison), use_container_width=True)
            
            # Market share visualization
            st.subheader("📈 Market Share Analysis (Based on Revenue)")
            
            market_data = []
            for company in company_datasets:
                df_comp = company['data']
                if 'Revenue' in df_comp.columns:
                    if 'Year' in df_comp.columns:
                        df_comp = df_comp[df_comp['Year'] == 2025]
                    total_rev = df_comp['Revenue'].sum()
                    market_data.append({
                        'company': company['name'],
                        'revenue': total_rev
                    })
            
            if market_data:
                fig_market = px.pie(
                    pd.DataFrame(market_data),
                    values='revenue',
                    names='company',
                    title='Revenue Market Share Distribution'
                )
                st.plotly_chart(fig_market, use_container_width=True)
            
            st.markdown("---")
            st.info("💡 **Tip:** Upload CSV files with the same column structure for accurate comparisons. The comparison uses 2025 data when Year column is available.")
            
        else:
            st.warning("⚠️ Please upload at least 2 company datasets for comparison.")
        
        return  # Exit early in multi-company mode
    
    # Apply quarter filter
    if filters['selected_quarters'] and 'Quarter' in df.columns:
        df = df[df['Quarter'].isin(filters['selected_quarters'])]
    
    if df.empty:
        st.warning("No data available for selected filters. Please adjust your filter settings.")
        return
    
    # Calculate metrics
    metrics = calculate_metrics(df)
    
    # Key metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Revenue",
            value=f"${metrics['total_revenue']:,.0f}",
            delta=f"{metrics['growth_rate']:.1f}% growth"
        )
    
    with col2:
        st.metric(
            label="💵 Net Profit",
            value=f"${metrics['total_profit']:,.0f}",
            delta=f"{(metrics['total_profit']/metrics['total_revenue']*100):.1f}% of revenue"
        )
    
    with col3:
        st.metric(
            label="📈 Avg Operating Margin",
            value=f"{metrics['avg_margin']:.1%}",
            delta="Quarterly average"
        )
    
    with col4:
        st.metric(
            label="📊 Growth Rate",
            value=f"{metrics['growth_rate']:.1f}%",
            delta="Q1 to Q4 2025"
        )
    
    # Charts section
    st.markdown("---")
    
    # Revenue and Profit Trend
    if filters['show_revenue']:
        st.subheader("📈 Revenue & Profit Trends")
        
        fig_revenue = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Revenue bars
        fig_revenue.add_trace(
            go.Bar(
                x=df['Quarter'],
                y=df['Revenue'],
                name='Revenue',
                marker_color='#3498db',
                opacity=0.8
            ),
            secondary_y=False,
        )
        
        # Net Profit line
        fig_revenue.add_trace(
            go.Scatter(
                x=df['Quarter'],
                y=df['Net_Profit'],
                mode='lines+markers',
                name='Net Profit',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=8)
            ),
            secondary_y=True,
        )
        
        fig_revenue.update_xaxes(title_text="Quarter")
        fig_revenue.update_yaxes(title_text="Revenue ($)", secondary_y=False)
        fig_revenue.update_yaxes(title_text="Net Profit ($)", secondary_y=True)
        fig_revenue.update_layout(
            title="Quarterly Revenue vs Net Profit",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Expense Breakdown and Margins
    if filters['show_expenses'] or filters['show_margins']:
        col1, col2 = st.columns(2)
        
        if filters['show_expenses']:
            with col1:
                st.subheader("💸 Expense Breakdown")
                
                # Calculate total expenses for pie chart
                expense_data = {
                    'Operating': df['Operating_Expenses'].sum(),
                    'Marketing': df['Marketing_Expenses'].sum(),
                    'R&D': df['R&D_Expenses'].sum(),
                    'Administrative': df['Administrative_Expenses'].sum()
                }
                
                fig_pie = px.pie(
                    values=list(expense_data.values()),
                    names=list(expense_data.keys()),
                    title="Total Expenses Distribution 2025",
                    color_discrete_sequence=['#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        if filters['show_margins']:
            with col2:
                st.subheader("📊 Margin Analysis")
                
                fig_margin = go.Figure()
                
                fig_margin.add_trace(go.Scatter(
                    x=df['Quarter'],
                    y=df['Gross_Margin'],
                    mode='lines+markers',
                    name='Gross Margin',
                    line=dict(color='#2ecc71', width=3),
                    marker=dict(size=8)
                ))
                
                fig_margin.add_trace(go.Scatter(
                    x=df['Quarter'],
                    y=df['Operating_Margin'],
                    mode='lines+markers',
                    name='Operating Margin',
                    line=dict(color='#3498db', width=3),
                    marker=dict(size=8)
                ))
                
                fig_margin.update_layout(
                    title="Quarterly Margin Trends",
                    xaxis_title="Quarter",
                    yaxis_title="Margin (%)",
                    yaxis=dict(tickformat='.1%'),
                    height=400,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_margin, use_container_width=True)
    
    # Business Metrics
    if filters['show_business']:
        st.subheader("🎯 Business Growth Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_users = px.bar(
                df,
                x='Quarter',
                y='Monthly_Active_Users',
                title='Monthly Active Users Growth',
                color='Monthly_Active_Users',
                color_continuous_scale='Blues'
            )
            fig_users.update_layout(height=350)
            st.plotly_chart(fig_users, use_container_width=True)
        
        with col2:
            fig_employees = px.line(
                df,
                x='Quarter',
                y='Employee_Count',
                title='Employee Growth',
                markers=True,
                line_shape='spline'
            )
            fig_employees.update_traces(
                line_color='#e67e22',
                marker_size=10
            )
            fig_employees.update_layout(height=350)
            st.plotly_chart(fig_employees, use_container_width=True)
    
    # Year-over-Year Comparison
    if filters['show_yoy'] and 'Year' in df.columns:
        st.markdown("---")
        st.subheader("📊 Year-over-Year Comparison (2024 vs 2025)")
        
        # Split data by year
        df_2024 = df[df['Year'] == 2024].copy()
        df_2025 = df[df['Year'] == 2025].copy()
        
        if not df_2024.empty and not df_2025.empty:
            # Calculate YoY metrics
            total_rev_2024 = df_2024['Revenue'].sum()
            total_rev_2025 = df_2025['Revenue'].sum()
            yoy_revenue_growth = ((total_rev_2025 - total_rev_2024) / total_rev_2024) * 100
            
            total_profit_2024 = df_2024['Net_Profit'].sum()
            total_profit_2025 = df_2025['Net_Profit'].sum()
            yoy_profit_growth = ((total_profit_2025 - total_profit_2024) / total_profit_2024) * 100
            
            # YoY metrics cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Revenue Growth YoY",
                    value=f"{yoy_revenue_growth:.1f}%",
                    delta=f"${total_rev_2025 - total_rev_2024:,.0f}"
                )
            
            with col2:
                st.metric(
                    label="Profit Growth YoY",
                    value=f"{yoy_profit_growth:.1f}%",
                    delta=f"${total_profit_2025 - total_profit_2024:,.0f}"
                )
            
            with col3:
                users_2024 = df_2024['Monthly_Active_Users'].iloc[-1]
                users_2025 = df_2025['Monthly_Active_Users'].iloc[-1]
                user_growth = ((users_2025 - users_2024) / users_2024) * 100
                st.metric(
                    label="User Growth YoY",
                    value=f"{user_growth:.1f}%",
                    delta=f"{users_2025 - users_2024:,} users"
                )
            
            with col4:
                emp_2024 = df_2024['Employee_Count'].iloc[-1]
                emp_2025 = df_2025['Employee_Count'].iloc[-1]
                emp_growth = ((emp_2025 - emp_2024) / emp_2024) * 100
                st.metric(
                    label="Employee Growth YoY",
                    value=f"{emp_growth:.1f}%",
                    delta=f"{emp_2025 - emp_2024:,} employees"
                )
            
            # YoY comparison charts
            col1, col2 = st.columns(2)
            
            # Extract quarter identifiers (e.g., 'Q1', 'Q2') from both years
            df_2024_copy = df_2024.copy()
            df_2025_copy = df_2025.copy()
            
            if 'Quarter' in df_2024_copy.columns:
                df_2024_copy['Quarter_ID'] = df_2024_copy['Quarter'].str.extract(r'(Q\d)')[0]
            if 'Quarter' in df_2025_copy.columns:
                df_2025_copy['Quarter_ID'] = df_2025_copy['Quarter'].str.extract(r'(Q\d)')[0]
            
            # Find common quarters between both years for fair comparison
            common_quarters = []
            if 'Quarter_ID' in df_2024_copy.columns and 'Quarter_ID' in df_2025_copy.columns:
                quarters_2024_set = set(df_2024_copy['Quarter_ID'].tolist())
                quarters_2025_set = set(df_2025_copy['Quarter_ID'].tolist())
                common_quarters = sorted(list(quarters_2024_set & quarters_2025_set))
            
            if common_quarters:
                # Filter both dataframes to only include common quarters
                df_2024_aligned = df_2024_copy[df_2024_copy['Quarter_ID'].isin(common_quarters)].sort_values('Quarter_ID')
                df_2025_aligned = df_2025_copy[df_2025_copy['Quarter_ID'].isin(common_quarters)].sort_values('Quarter_ID')
                
                with col1:
                    # Revenue comparison
                    fig_yoy_rev = go.Figure()
                    
                    fig_yoy_rev.add_trace(go.Bar(
                        name='2024',
                        x=df_2024_aligned['Quarter_ID'].tolist(),
                        y=df_2024_aligned['Revenue'].tolist(),
                        marker_color='#95a5a6'
                    ))
                    
                    fig_yoy_rev.add_trace(go.Bar(
                        name='2025',
                        x=df_2025_aligned['Quarter_ID'].tolist(),
                        y=df_2025_aligned['Revenue'].tolist(),
                        marker_color='#3498db'
                    ))
                    
                    fig_yoy_rev.update_layout(
                        title='Revenue Comparison: 2024 vs 2025',
                        xaxis_title='Quarter',
                        yaxis_title='Revenue ($)',
                        barmode='group',
                        height=400
                    )
                    
                    st.plotly_chart(fig_yoy_rev, use_container_width=True)
                
                with col2:
                    # Profit comparison
                    fig_yoy_profit = go.Figure()
                    
                    fig_yoy_profit.add_trace(go.Bar(
                        name='2024',
                        x=df_2024_aligned['Quarter_ID'].tolist(),
                        y=df_2024_aligned['Net_Profit'].tolist(),
                        marker_color='#95a5a6'
                    ))
                    
                    fig_yoy_profit.add_trace(go.Bar(
                        name='2025',
                        x=df_2025_aligned['Quarter_ID'].tolist(),
                        y=df_2025_aligned['Net_Profit'].tolist(),
                        marker_color='#2ecc71'
                    ))
                    
                    fig_yoy_profit.update_layout(
                        title='Net Profit Comparison: 2024 vs 2025',
                        xaxis_title='Quarter',
                        yaxis_title='Net Profit ($)',
                        barmode='group',
                        height=400
                    )
                    
                    st.plotly_chart(fig_yoy_profit, use_container_width=True)
            else:
                st.warning("⚠️ No common quarters found between 2024 and 2025 data after filtering. Please adjust your quarter selections to enable YoY comparison.")
    
    # Revenue Forecast Section
    if filters['show_forecast'] and 'Revenue' in df.columns and len(df) >= 4:
        st.markdown("---")
        st.subheader("🔮 Revenue Forecast - Predictive Analytics")
        
        # Get 2025 data for forecasting
        if 'Year' in df.columns:
            df_forecast_base = df[df['Year'] == 2025].copy()
        else:
            df_forecast_base = df.copy()
        
        if len(df_forecast_base) >= 3:
            # Simple linear regression forecast
            revenue_values = df_forecast_base['Revenue'].values
            x = np.arange(len(revenue_values))
            
            # Calculate linear regression coefficients
            z = np.polyfit(x, revenue_values, 1)
            p = np.poly1d(z)
            
            # Forecast next 4 quarters
            forecast_periods = 4
            future_x = np.arange(len(revenue_values), len(revenue_values) + forecast_periods)
            forecast_values = p(future_x)
            
            # Calculate confidence interval (simplified)
            residuals = revenue_values - p(x)
            std_error = np.std(residuals)
            confidence_margin = 1.96 * std_error  # 95% confidence interval
            
            # Create forecast visualization
            fig_forecast = go.Figure()
            
            # Historical data
            fig_forecast.add_trace(go.Scatter(
                x=df_forecast_base['Quarter'].tolist(),
                y=revenue_values,
                mode='lines+markers',
                name='Historical Revenue',
                line=dict(color='#3498db', width=3),
                marker=dict(size=10)
            ))
            
            # Forecast data
            forecast_quarters = ['Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026']
            fig_forecast.add_trace(go.Scatter(
                x=forecast_quarters,
                y=forecast_values,
                mode='lines+markers',
                name='Forecasted Revenue',
                line=dict(color='#e74c3c', width=3, dash='dash'),
                marker=dict(size=10, symbol='diamond')
            ))
            
            # Confidence interval
            fig_forecast.add_trace(go.Scatter(
                x=forecast_quarters,
                y=forecast_values + confidence_margin,
                mode='lines',
                name='Upper Bound (95% CI)',
                line=dict(color='rgba(231, 76, 60, 0.3)', width=1),
                showlegend=True
            ))
            
            fig_forecast.add_trace(go.Scatter(
                x=forecast_quarters,
                y=forecast_values - confidence_margin,
                mode='lines',
                name='Lower Bound (95% CI)',
                line=dict(color='rgba(231, 76, 60, 0.3)', width=1),
                fill='tonexty',
                fillcolor='rgba(231, 76, 60, 0.1)',
                showlegend=True
            ))
            
            fig_forecast.update_layout(
                title='Revenue Forecast for 2026 (Based on 2025 Trend)',
                xaxis_title='Quarter',
                yaxis_title='Revenue ($)',
                height=500,
                hovermode='x unified',
                showlegend=True
            )
            
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            # Forecast metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_forecast = np.mean(forecast_values)
                st.metric(
                    label="Avg Forecast Revenue (2026)",
                    value=f"${avg_forecast:,.0f}",
                    delta=f"{((avg_forecast - np.mean(revenue_values)) / np.mean(revenue_values) * 100):.1f}% vs 2025 avg"
                )
            
            with col2:
                total_forecast = np.sum(forecast_values)
                st.metric(
                    label="Total Forecast Revenue (2026)",
                    value=f"${total_forecast:,.0f}",
                    delta=f"${total_forecast - np.sum(revenue_values):,.0f} vs 2025"
                )
            
            with col3:
                growth_rate = ((forecast_values[-1] - revenue_values[-1]) / revenue_values[-1]) * 100
                st.metric(
                    label="Projected Growth Rate",
                    value=f"{growth_rate:.1f}%",
                    delta="Q4 2025 to Q4 2026"
                )
            
            # Forecast insights
            st.info(f"📊 **Forecast Insights:** Based on 2025 performance trends, revenue is projected to grow at an average rate of {z[0]/1000000:.1f}M per quarter. The 95% confidence interval suggests revenue could range from ${(forecast_values[0] - confidence_margin)/1000000:.1f}M to ${(forecast_values[0] + confidence_margin)/1000000:.1f}M in Q1 2026.")
    
    # Data table
    st.markdown("---")
    st.subheader("📋 Raw Financial Data")
    
    # Format the dataframe for display
    display_df = df.copy()
    
    # Format currency columns
    currency_cols = ['Revenue', 'Operating_Expenses', 'Marketing_Expenses', 
                    'R&D_Expenses', 'Administrative_Expenses', 'Net_Profit']
    
    for col in currency_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
    
    # Format percentage columns
    percentage_cols = ['Gross_Margin', 'Operating_Margin']
    for col in percentage_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.1%}")
    
    # Format number columns
    number_cols = ['Monthly_Active_Users', 'Employee_Count']
    for col in number_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:,}")
    
    st.dataframe(display_df, use_container_width=True)
    
    # PDF Download Section
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📥 Download PDF Report", use_container_width=True, type="primary"):
            pdf_buffer = generate_pdf_report(df, metrics)
            st.download_button(
                label="💾 Save PDF Report",
                data=pdf_buffer,
                file_name=f"financial_dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# PDF Report Generation
def generate_pdf_report(df, metrics):
    """Generate a PDF report of the financial dashboard"""
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph("Tech Company Financial Dashboard 2025", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Report metadata
    report_date = Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                            styles['Normal'])
    elements.append(report_date)
    elements.append(Spacer(1, 20))
    
    # Key Metrics Section
    metrics_heading = Paragraph("Key Financial Metrics", heading_style)
    elements.append(metrics_heading)
    
    metrics_data = [
        ['Metric', 'Value'],
        ['Total Revenue', f"${metrics['total_revenue']:,.0f}"],
        ['Net Profit', f"${metrics['total_profit']:,.0f}"],
        ['Avg Operating Margin', f"{metrics['avg_margin']:.1%}"],
        ['Growth Rate (Q1 to Q4)', f"{metrics['growth_rate']:.1f}%"],
        ['Profit Margin', f"{(metrics['total_profit']/metrics['total_revenue']*100):.1f}%"]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(metrics_table)
    elements.append(Spacer(1, 20))
    
    # Financial Data Table
    data_heading = Paragraph("Quarterly Financial Data", heading_style)
    elements.append(data_heading)
    
    # Prepare data table
    table_data = [['Quarter', 'Revenue ($M)', 'Net Profit ($M)', 'Operating Margin']]
    
    for _, row in df.iterrows():
        if 'Quarter' in row and 'Revenue' in row:
            table_data.append([
                str(row['Quarter']),
                f"${row['Revenue']/1000000:.1f}M",
                f"${row['Net_Profit']/1000000:.1f}M" if 'Net_Profit' in row else 'N/A',
                f"{row['Operating_Margin']:.1%}" if 'Operating_Margin' in row else 'N/A'
            ])
    
    data_table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    elements.append(data_table)
    elements.append(Spacer(1, 30))
    
    # Footer
    footer_text = Paragraph(
        "© 2025 Girish Lade. All rights reserved. | Powered by <a href='https://ladestack.in'>LadeStack.in</a>",
        styles['Normal']
    )
    elements.append(footer_text)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer

# Footer
def render_footer():
    """Render footer with copyright and backlink"""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>© 2025 Girish Lade. All rights reserved. | 
            <a href='https://ladestack.in' target='_blank' style='color: #3498db;'>
                Powered by LadeStack.in
            </a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Main application
def main():
    """Main application function"""
    
    # Load initial data to show filters
    df_initial = load_data(None)
    
    # Render sidebar and get filters
    filters = render_sidebar(df_initial)
    
    # Load data with uploaded file if provided
    df = load_data(filters['uploaded_file'])
    
    # Render dashboard with filters
    render_dashboard(df, filters)
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
