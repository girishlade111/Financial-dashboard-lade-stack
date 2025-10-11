import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

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
    """Load mock financial data for 2025"""
    data = {
        'Quarter': ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025'],
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
    return pd.DataFrame(data)

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

# Sidebar with contact information
def render_sidebar():
    """Render sidebar with contact information and file upload"""
    st.sidebar.markdown("## 📊 Financial Dashboard")
    st.sidebar.markdown("---")
    
    # File upload
    st.sidebar.markdown("### Upload CSV Data")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="Upload your financial data CSV to replace mock data"
    )
    
    st.sidebar.markdown("---")
    
    # Contact information
    st.sidebar.markdown("### 📞 Contact Information")
    st.sidebar.markdown("**Girish Lade**")
    st.sidebar.markdown("📧 [girish@ladestack.in](mailto:girish@ladestack.in)")
    st.sidebar.markdown("📱 [Instagram: @girish_lade_](https://instagram.com/girish_lade_)")
    st.sidebar.markdown("💻 [GitHub: girishlade111](https://github.com/girishlade111)")
    st.sidebar.markdown("🌐 [Visit LadeStack.in](https://ladestack.in)")
    
    return uploaded_file

# Main dashboard content
def render_dashboard(df):
    """Render main dashboard content"""
    
    # Title and description
    st.title("🚀 Tech Company Financial Dashboard 2025")
    st.markdown("Interactive financial analytics and performance metrics")
    
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
    
    # Expense Breakdown
    col1, col2 = st.columns(2)
    
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
    
    # Render sidebar and get uploaded file
    uploaded_file = render_sidebar()
    
    # Load data
    df = load_data(uploaded_file)
    
    # Render dashboard
    render_dashboard(df)
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
