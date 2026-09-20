import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from groq import Groq

st.set_page_config(page_title="FinPilot - AI Personal Finance Agent", layout="wide")

# CSS Styling for Continuous Looping Financial Facts Carousel
st.markdown("""
<style>
.carousel-container {
    width: 100%;
    background-color: #0F172A;
    color: #F8FAFC;
    padding: 12px 20px;
    border-radius: 8px;
    margin-bottom: 25px;
    border-left: 5px solid #3B82F6;
    overflow: hidden;
    white-space: nowrap;
}
.carousel-text {
    display: inline-block;
    padding-left: 100%;
    animation: marquee 24s linear infinite;
    font-weight: 500;
    font-size: 15px;
}
@keyframes marquee {
    0%   { transform: translate(0, 0); }
    100% { transform: translate(-100%, 0); }
}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ FinPilot: AI Personal Finance Decision Support Agent")
st.caption("Agentic Cash-Flow Engineering, Subscription Vampire Detection & 12-Month Financial Intelligence")

# 1. Financial Facts Carousel
facts = [
    "💡 **Rule of 72:** Divide 72 by your expected annual return rate to estimate years to double your investment.",
    "⚠️ **Subscription Leakage:** Consumers underestimate monthly recurring subscriptions by over 100% on average.",
    "🛡️ **Emergency Fund Benchmark:** Keep 3 to 6 months of committed obligations in liquid cash.",
    "📊 **50/30/20 Rule:** Allocate 50% to Needs, 30% to Wants, and 20% to Savings & Debt Repayment."
]
carousel_html = f'<div class="carousel-container"><div class="carousel-text"> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; '.join(facts) + '</div></div>'
st.markdown(carousel_html, unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Agent Settings")
    api_key = st.text_input("Groq API Key", type="password", value=os.environ.get("GROQ_API_KEY", ""))
    st.markdown("---")
    st.subheader("🎯 Target Financial Goal")
    goal_name = st.text_input("Goal Name", "Emergency Fund")
    goal_target = st.number_input("Target Amount ($)", value=5000.0)
    monthly_savings_goal = st.number_input("Monthly Savings Target ($)", value=500.0)
    
    st.markdown("---")
    st.subheader("🏦 Loan / EMI Parameters")
    total_loan_amount = st.number_input("Total Loan Principal ($)", value=25000.0)
    monthly_emi = st.number_input("Monthly EMI ($)", value=450.0)
    remaining_tenure = st.number_input("Remaining Tenure (Months)", value=36)

# Main Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📊 Current Statement & Visuals", "📈 12-Month Trends & EMI Tracker", "🤖 Agentic Reasoning & QA"])

# Mock 12-Month Dataset Engine
np.random.seed(42)
months = ["Oct '25", "Nov '25", "Dec '25", "Jan '26", "Feb '26", "Mar '26", "Apr '26", "May '26", "Jun '26", "Jul '26", "Aug '26", "Sep '26"]
hist_expenses = np.random.randint(2800, 3600, size=12)
hist_savings = np.random.randint(400, 900, size=12)
hist_emi = [monthly_emi] * 12
df_12m = pd.DataFrame({
    "Month": months,
    "Expenses": hist_expenses,
    "Savings": hist_savings,
    "EMI Paid": hist_emi
})

with tab1:
    st.subheader("1. Statement Data Ingestion")
    uploaded_file = st.file_uploader("Upload CSV Bank Statement", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        st.info("Loaded default monthly transaction dataset.")
        df = pd.read_csv("sample_transactions.csv")

    st.dataframe(df, use_container_width=True)

    # Core Cash Flow Math
    total_income = df[df['Type'] == 'Credit']['Amount'].sum()
    total_expenses = df[df['Type'] == 'Debit']['Amount'].sum()
    recurring_expenses = df[df['Category'].isin(['Subscriptions', 'Housing', 'Utilities', 'Fitness'])]['Amount'].sum()
    free_to_spend = total_income - total_expenses

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Income", f"${total_income:,.2f}")
    c2.metric("Total Expenses", f"${total_expenses:,.2f}")
    c3.metric("Committed Obligations", f"${recurring_expenses:,.2f}")
    c4.metric("Free-to-Spend Buffer", f"${free_to_spend:,.2f}")

    st.markdown("---")
    st.subheader("2. Interactive Visualizations")
    
    col_pie, col_bar = st.columns(2)
    debit_df = df[df['Type'] == 'Debit']
    cat_summary = debit_df.groupby('Category')['Amount'].sum().reset_index()
    
    with col_pie:
        fig_pie = px.pie(cat_summary, values='Amount', names='Category', title='Spending Breakdown by Category', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_bar:
        fig_bar = px.bar(debit_df, x='Description', y='Amount', color='Category', title='Individual Expenses', text_auto='.2f')
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.subheader("12-Month Expense, Savings & EMI Analytics")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("12-Month Cumulative Savings", f"${df_12m['Savings'].sum():,.2f}")
    m2.metric("12-Month Total Expenses", f"${df_12m['Expenses'].sum():,.2f}")
    m3.metric("12-Month Total EMI Paid", f"${df_12m['EMI Paid'].sum():,.2f}")
    
    st.markdown("---")
    
    # 12-Month Multi-Metric Bar Chart
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Bar(x=df_12m['Month'], y=df_12m['Expenses'], name='Expenses', marker_color='#EF4444'))
    fig_hist.add_trace(go.Bar(x=df_12m['Month'], y=df_12m['Savings'], name='Savings', marker_color='#10B981'))
    fig_hist.add_trace(go.Bar(x=df_12m['Month'], y=df_12m['EMI Paid'], name='Loan EMI', marker_color='#F59E0B'))
    fig_hist.update_layout(barmode='group', title='12-Month Cash Flow & Loan EMI Breakdown', xaxis_title='Month', yaxis_title='Amount ($)')
    st.plotly_chart(fig_hist, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Cumulative Savings Growth Curve")
    df_12m['Cumulative_Savings'] = df_12m['Savings'].cumsum()
    fig_line = px.line(df_12m, x='Month', y='Cumulative_Savings', title='12-Month Cumulative Savings Progress', markers=True, line_shape='spline')
    fig_line.update_traces(line_color='#10B981', line_width=3)
    st.plotly_chart(fig_line, use_container_width=True)

with tab3:
    st.subheader("Multi-Agent Intelligence Engine & Natural Language Copilot")
    
    if api_key:
        client = Groq(api_key=api_key)
        
        if st.button("🚀 Trigger Agentic Analysis"):
            with st.spinner("Analyzing transaction ledger, subscription creep, loan commitments, and 12-month performance..."):
                prompt = f"""
                You are FinPilot, an expert financial decision-support AI agent.
                Analyze this financial profile:
                - Current Monthly Transactions: {df.to_dict(orient='records')}
                - 12-Month Total Expenses: ${df_12m['Expenses'].sum()}
                - 12-Month Total Savings: ${df_12m['Savings'].sum()}
                - Active Loan EMI: ${monthly_emi}/month ({remaining_tenure} months remaining)
                - Goal: {goal_name}, Target Amount: ${goal_target}, Target Monthly Allocation: ${monthly_savings_goal}
                
                Provide a structured report with these sections:
                1. **Subscription Vampire & Anomaly Detection**: Flag recurring charges, unexpected price jumps, or single spending spikes.
                2. **Cash-Flow & EMI Impact**: Assess how loan EMIs strain the Free-to-Spend buffer.
                3. **Goal Stress-Test**: Evaluate whether current savings velocity will achieve the ${goal_target} goal on time.
                4. **Actionable Recommendations**: Give 3 concrete steps to optimize monthly cash flow.
                """
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile"
                )
                st.markdown(response.choices[0].message.content)
                
        st.markdown("---")
        st.subheader("Natural Language Financial QA")
        user_query = st.text_input("Ask FinPilot a direct question about your money:", "Where did I spend the most this month?")
        
        if user_query:
            qa_prompt = f"""
            Answer the user's question directly based on this context:
            Transactions: {df.to_dict(orient='records')}
            12-Month Summary: Expenses = ${df_12m['Expenses'].sum()}, Savings = ${df_12m['Savings'].sum()}, Total EMI Paid = ${df_12m['EMI Paid'].sum()}
            
            Question: {user_query}
            Provide a concise, direct answer with exact numerical figures.
            """
            qa_res = client.chat.completions.create(
                messages=[{"role": "user", "content": qa_prompt}],
                model="llama-3.3-70b-versatile"
            )
            st.info(qa_res.choices[0].message.content)
    else:
        st.warning("Please enter a Groq API Key in the sidebar to run agentic features.")