import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from datetime import datetime
from groq import Groq

st.set_page_config(page_title="FinPilot - AI Personal Finance Agent", layout="wide")

# Custom CSS for Clean Financial Wisdom Box & Big Numbers
st.markdown("""
<style>
.wisdom-box {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    color: #F8FAFC;
    padding: 16px 22px;
    border-radius: 10px;
    margin-bottom: 25px;
    border-left: 6px solid #3B82F6;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.wisdom-title {
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #94A3B8;
    margin-bottom: 4px;
    font-weight: 700;
}
.wisdom-content {
    font-size: 16px;
    font-weight: 500;
    color: #F1F5F9;
}
.big-metric {
    font-size: 42px;
    font-weight: 800;
    color: #3B82F6;
    line-height: 1.1;
}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ FinPilot: AI Personal Finance Decision Support Agent")
st.caption("Intelligent Monthly Savings, Goal Tracker, Loan Amortization & Cash-Flow Engineering")

# Initialize Session States with Rupee defaults
if 'goals_list' not in st.session_state:
    st.session_state['goals_list'] = [
        {"name": "Emergency Fund", "target": 400000.0, "monthly_target": 25000.0},
        {"name": "New Car Down Payment", "target": 650000.0, "monthly_target": 40000.0}
    ]

if 'loan_saved' not in st.session_state:
    st.session_state['loan_saved'] = {
        "for": "Home / Personal Loan",
        "principal": 2000000.0,
        "emi": 35000.0,
        "tenure": 36,
        "start_date": "2025-10-01"
    }

# Single-Message Financial Wisdom Banner
import random
if 'fact_index' not in st.session_state:
    st.session_state['fact_index'] = random.randint(0, 3)

facts = [
    "💡 **Rule of 72:** Divide 72 by your expected annual return rate to estimate years required to double your investment.",
    "⚠️ **Subscription Leakage:** The average person underestimates their monthly recurring subscription spending by over 100%.",
    "🛡️ **Emergency Fund Benchmark:** Financial advisors recommend keeping 3 to 6 months of committed expenses in liquid cash.",
    "📊 **50/30/20 Rule:** Allocate 50% to Needs, 30% to Wants, and 20% directly toward Savings & Debt Amortization."
]
current_fact = facts[st.session_state['fact_index']]

st.markdown(f"""
<div class="wisdom-box">
    <div class="wisdom-title">💡 FinSmart Daily Financial Wisdom</div>
    <div class="wisdom-content">{current_fact}</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration for Goals
with st.sidebar:
    st.header("⚙️ User Configuration")
    api_key = st.text_input("Groq API Key", type="password", value=os.environ.get("GROQ_API_KEY", ""))
    
    st.markdown("---")
    st.subheader("🎯 Add Financial Goal")
    new_goal_name = st.text_input("Goal Name", placeholder="e.g., Vacation, Laptop")
    new_goal_target = st.number_input("Target Amount (₹)", value=150000.0, step=10000.0)
    new_goal_monthly = st.number_input("Monthly Savings Target (₹)", value=15000.0, step=1000.0)
    
    if st.button("➕ Add Goal"):
        if new_goal_name:
            st.session_state['goals_list'].append({
                "name": new_goal_name,
                "target": new_goal_target,
                "monthly_target": new_goal_monthly
            })
            st.success(f"Added goal: {new_goal_name}")
            st.rerun()

# Main Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📊 Current Statement, Savings & Goals", "📈 12-Month Trends & Loan Status", "🤖 Agentic Reasoning & QA"])

with tab1:
    st.subheader("1. Monthly Statement Ingestion")
    uploaded_file = st.file_uploader("Upload CSV Expense Statement for Month-End Review", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        st.info("Loaded default monthly transaction dataset.")
        df = pd.DataFrame({
            "Date": ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-05", "2026-09-07", "2026-09-10", "2026-09-12", "2026-09-14", "2026-09-15", "2026-09-18"],
            "Description": ["Salary Income", "Apartment Rent", "Whole Foods Market", "Netflix Subscription", "Spotify Premium", "Tech Gadgets Store", "Electric Utility Bill", "Uber Rides", "Gym Membership", "Restaurant Dinner"],
            "Category": ["Income", "Housing", "Groceries", "Subscriptions", "Subscriptions", "Shopping", "Utilities", "Transport", "Fitness", "Dining"],
            "Amount": [400000.00, 120000.00, 12000.00, 799.00, 299.00, 35000.00, 9500.00, 3500.00, 4000.00, 7500.00],
            "Type": ["Credit", "Debit", "Debit", "Debit", "Debit", "Debit", "Debit", "Debit", "Debit", "Debit"]
        })

    st.dataframe(df, use_container_width=True)

    # Core Cash Flow Math (Savings this month)
    total_income = df[df['Type'] == 'Credit']['Amount'].sum()
    total_expenses = df[df['Type'] == 'Debit']['Amount'].sum()
    recurring_expenses = df[df['Category'].isin(['Subscriptions', 'Housing', 'Utilities', 'Fitness'])]['Amount'].sum()
    savings_this_month = total_income - total_expenses

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Income", f"₹{total_income:,.2f}")
    c2.metric("Total Expenses", f"₹{total_expenses:,.2f}")
    c3.metric("Committed Obligations", f"₹{recurring_expenses:,.2f}")
    c4.metric("Savings This Month", f"₹{savings_this_month:,.2f}")

    st.markdown("---")
    st.subheader("2. Financial Goals Progress (Current Month)")
    
    # Distribute savings dynamically across goals
    total_goals_count = len(st.session_state['goals_list'])
    distributed_pool = max(0.0, savings_this_month) / total_goals_count if total_goals_count > 0 else 0.0

    if total_goals_count == 0:
        st.info("No financial goals added yet. Add some in the sidebar!")
    else:
        goal_cols = st.columns(total_goals_count)
        for idx, goal in enumerate(st.session_state['goals_list']):
            with goal_cols[idx]:
                # Dynamic distribution per goal
                this_month_saved_for_goal = min(distributed_pool, goal['monthly_target'])
                target_met = this_month_saved_for_goal >= goal['monthly_target']
                
                status_label = "🟢 Target Reached!" if target_met else "⏳ In Progress"
                
                st.markdown(f"**🎯 {goal['name']}**")
                st.write(f"Target Pool: ₹{goal['target']:,.2f}")
                st.write(f"Monthly Needed: ₹{goal['monthly_target']:,.2f}")
                st.write(f"This Month Saved: **₹{this_month_saved_for_goal:,.2f}**")
                st.markdown(f"Status: **{status_label}**")
                
                progress_val = min(float(this_month_saved_for_goal / goal['monthly_target']), 1.0) if goal['monthly_target'] > 0 else 0.0
                st.progress(progress_val)

    st.markdown("---")
    st.subheader("3. Interactive Expense Visualizations")
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
    st.subheader("12-Month Expense, Savings & Loan EMI Analytics")
    
    # Loan & EMI Tracker moved directly inside tab 2
    with st.expander("🏦 Configure & Manage Loan Details", expanded=True):
        col_l1, col_l2, col_l3, col_l4 = st.columns(4)
        with col_l1:
            loan_for_input = st.text_input("Loan For (Purpose)", value=st.session_state['loan_saved']['for'])
        with col_l2:
            loan_principal_input = st.number_input("Total Loan Principal (₹)", value=st.session_state['loan_saved']['principal'], step=50000.0)
        with col_l3:
            loan_emi_input = st.number_input("Monthly EMI (₹)", value=st.session_state['loan_saved']['emi'], step=5000.0)
        with col_l4:
            loan_tenure_input = st.number_input("Total Tenure (Months)", value=st.session_state['loan_saved']['tenure'], step=1)
        
        if st.button("💾 Save Loan Details"):
            st.session_state['loan_saved'] = {
                "for": loan_for_input,
                "principal": loan_principal_input,
                "emi": loan_emi_input,
                "tenure": loan_tenure_input,
                "start_date": "2025-10-01"
            }
            st.success("Loan details updated successfully!")

    st.markdown("---")

    # Mock 12-Month Dataset synchronized with loan parameters in Rupees
    np.random.seed(42)
    months = ["Oct '25", "Nov '25", "Dec '25", "Jan '26", "Feb '26", "Mar '26", "Apr '26", "May '26", "Jun '26", "Jul '26", "Aug '26", "Sep '26"]
    hist_expenses = np.random.randint(220000, 280000, size=12)
    hist_savings = np.random.randint(40000, 90000, size=12)
    
    active_emi = st.session_state['loan_saved']['emi']
    hist_emi = [active_emi] * 12
    
    df_12m = pd.DataFrame({
        "Month": months,
        "Expenses": hist_expenses,
        "Savings": hist_savings,
        "EMI Paid": hist_emi
    })
    
    m1, m2, m3 = st.columns(3)
    m1.metric("12-Month Cumulative Savings", f"₹{df_12m['Savings'].sum():,.2f}")
    m2.metric("12-Month Total Expenses", f"₹{df_12m['Expenses'].sum():,.2f}")
    m3.metric("Total EMI Paid (12M)", f"₹{df_12m['EMI Paid'].sum():,.2f}")
    
    st.markdown("---")
    
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Bar(x=df_12m['Month'], y=df_12m['Expenses'], name='Expenses', marker_color='#EF4444'))
    fig_hist.add_trace(go.Bar(x=df_12m['Month'], y=df_12m['Savings'], name='Savings', marker_color='#10B981'))
    fig_hist.add_trace(go.Bar(x=df_12m['Month'], y=df_12m['EMI Paid'], name='Loan EMI', marker_color='#F59E0B'))
    fig_hist.update_layout(barmode='group', title='12-Month Cash Flow & Aggregated Loan EMI Tracking', xaxis_title='Month', yaxis_title='Amount (₹)')
    st.plotly_chart(fig_hist, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🏦 Loan Closure & Timeline Summary")
    
    loan_info = st.session_state['loan_saved']
    start_dt = datetime.strptime(loan_info['start_date'], "%Y-%m-%d")
    current_dt = datetime.now()
    months_elapsed = max(1, (current_dt.year - start_dt.year) * 12 + (current_dt.month - start_dt.month))
    remaining_months = max(0, loan_info['tenure'] - months_elapsed)
    total_remaining_liability = remaining_months * loan_info['emi']

    l_col1, l_col2, l_col3 = st.columns(3)
    with l_col1:
        st.markdown(f"**Loan Purpose:** {loan_info['for']}")
        st.write(f"Original Principal: ₹{loan_info['principal']:,.2f}")
        st.write(f"Monthly EMI: ₹{loan_info['emi']:,.2f}")
    with l_col2:
        st.markdown("**Months Active (Since Started):**")
        st.markdown(f"<div class='big-metric'>{months_elapsed} Months</div>", unsafe_allow_html=True)
    with l_col3:
        st.markdown("**Months Remaining for Closure:**")
        st.markdown(f"<div class='big-metric'>{remaining_months} Months</div>", unsafe_allow_html=True)
        st.caption(f"Estimated Remaining Liability: ₹{total_remaining_liability:,.2f}")

with tab3:

    st.subheader("Multi-Agent Intelligence Engine & Natural Language Copilot")
    
    if api_key:
        client = Groq(api_key=api_key)
        
        if st.button("🚀 Trigger Agentic Analysis"):
            with st.spinner("Analyzing savings, goals progress, loan schedule, and expenses..."):
                prompt = f"""
                You are FinPilot, an expert financial decision-support AI agent.
                Analyze this financial status:
                - Savings This Month: ₹{savings_this_month}
                - Active Loan: {st.session_state['loan_saved']['for']}, EMI: ₹{st.session_state['loan_saved']['emi']}/mo, Remaining Months: {remaining_months}
                - Goals List: {st.session_state['goals_list']}
                
                Provide a structured report covering:
                1. **Monthly Savings Health**: Review the savings vs monthly goals.
                2. **Loan Amortization Impact**: Assess how the EMI affects long-term runway.
                3. **Actionable Recommendations**: Give 3 tips to accelerate goal achievement.
                """
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant"
                )
                st.markdown(response.choices[0].message.content)
                
        st.markdown("---")
        st.subheader("Natural Language Financial QA")
        user_query = st.text_input("Ask FinPilot a direct question about your money:", "Did I save enough for my goals this month?")
        
        if user_query:
            qa_prompt = f"""
            Answer accurately based on this context:
            Savings This Month: ₹{savings_this_month}
            Goals: {st.session_state['goals_list']}
            Loan: {st.session_state['loan_saved']}
            
            Question: {user_query}
            Provide a concise, direct answer with exact numbers in Rupees.
            """
            qa_res = client.chat.completions.create(
                messages=[{"role": "user", "content": qa_prompt}],
                model="llama-3.1-8b-instant"
            )
            st.info(qa_res.choices[0].message.content)
    else:
        st.warning("Please enter a Groq API Key in the sidebar to run agentic features.")