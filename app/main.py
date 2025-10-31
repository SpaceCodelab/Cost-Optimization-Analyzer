import streamlit as st
from core.aws import get_aws_costs
from core.analyzer import find_savings
import plotly.express as px

st.set_page_config(page_title="Cost Optimizer", layout="wide")
st.title("Cloud Cost Optimization Analyzer")

tab1, tab2, tab3 = st.tabs(["Upload", "AWS", "GCP"])

with tab1:
    uploaded = st.file_uploader("Drop AWS/GCP CSV", type=['csv'])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.success("Loaded!")

with tab2:
    if st.button("Fetch AWS Costs (30 days)"):
        with st.spinner("Pulling data..."):
            df = get_aws_costs()
            st.session_state.df = df
    if 'df' in st.session_state:
        df = st.session_state.df
        fig = px.bar(df, x='Date', y='Cost', color='Service', title="Daily Spend")
        st.plotly_chart(fig, use_container_width=True)

        savings = find_savings(df)
        st.subheader("Savings Opportunities")
        st.dataframe(savings.style.format({'potential_saving': '${:,.2f}'}))

        csv = savings.to_csv(index=False)
        st.download_button("Export Report", csv, "savings.csv", "text/csv")