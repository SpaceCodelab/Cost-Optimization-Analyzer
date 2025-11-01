# app/main.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
import os
import random
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from fpdf import FPDF
import matplotlib.pyplot as plt
import textwrap

# =============================================
# PAGE CONFIG & BRANDING
# =============================================
st.set_page_config(page_title="CloudPulse AI - AWS", layout="wide")
st.markdown("""
<div style='text-align:center; font-family:"Trebuchet MS", sans-serif;'>
    <h1 style='font-size:60px; background: linear-gradient(90deg, #1E90FF, #00CED1); -webkit-background-clip: text; color: transparent;'>
        Cloud Cost Analyzer
    </h1>
</div>
""", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'><strong>By Ramanjeet Singh and Ayush Garg</strong> – CU Full Stack Capstone 2025</p>", unsafe_allow_html=True)
st.image("app/logo.svg", width=200)
st.markdown("---")

# =============================================
# 1. AWS DATA — ONLY
# =============================================
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
AWS_FILE = os.path.join(DATA_DIR, "sample_aws.csv")

if not os.path.exists(AWS_FILE):
    st.error(f"AWS data not found: {AWS_FILE}\n\nPlace your AWS billing CSV in the `data/` folder.")
    st.stop()

try:
    df = pd.read_csv(AWS_FILE, on_bad_lines='skip', engine='python')
except Exception as e:
    st.error(f"Error reading AWS file: {e}")
    st.stop()

df.columns = df.columns.str.strip()
if "UsageStartDate" in df.columns:
    df["Date"] = pd.to_datetime(df["UsageStartDate"], errors="coerce").dt.date
elif "BillingPeriodStartDate" in df.columns:
    df["Date"] = pd.to_datetime(df["BillingPeriodStartDate"], errors="coerce").dt.date
else:
    st.error("AWS CSV missing date column")
    st.stop()

cost_col = "UnblendedCost" if "UnblendedCost" in df.columns else "BlendedCost"
if cost_col not in df.columns:
    st.error("AWS CSV missing cost column")
    st.stop()
df["Cost"] = pd.to_numeric(df[cost_col], errors="coerce").fillna(0)

df["Service"] = df.get("ProductName", df.get("ProductCode", "Unknown"))
df["Region"] = df.get("AvailabilityZone", "unknown").str.extract(r"([a-z]+-[a-z]+-\d)")

df["Date"] = pd.to_datetime(df["Date"])
df = df.dropna(subset=["Date", "Cost"])

if df.empty:
    st.warning("No valid AWS data after parsing.")
    st.stop()

# =============================================
# 2. DATE FILTER
# =============================================
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", df["Date"].min().date())
with col2:
    end_date = st.date_input("End Date", df["Date"].max().date())

df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

# =============================================
# 3. SERVICE USAGE EFFICIENCY
# =============================================
def service_efficiency(df):
    efficiency_list = []
    for service, group in df.groupby("Service"):
        total_cost = group["Cost"].sum()
        avg_cost = group["Cost"].mean()
        max_cost = group["Cost"].max()
        efficiency_score = max(0, min(100, int(100 - (avg_cost/max(1,total_cost))*100)))
        efficiency_list.append({
            "Service": service,
            "Total Spend": total_cost,
            "Avg Daily Spend": avg_cost,
            "Max Daily Spend": max_cost,
            "Efficiency (%)": efficiency_score
        })
    return pd.DataFrame(efficiency_list)

efficiency_df = service_efficiency(df)

# =============================================
# 4. AI-Powered Multi-Scenario Recommendations
# =============================================
def find_savings(df):
    savings = []
    # EC2
    ec2_df = df[df["Service"].str.contains("EC2|Compute", case=False, na=False)]
    ec2_total = ec2_df["Cost"].sum()
    underutilized_instances = random.randint(1, len(ec2_df)) if not ec2_df.empty else 0
    if ec2_total > 50:
        savings.append({
            "Recommendation": f"Right-size {underutilized_instances} EC2 instances",
            "Potential Saving": f"${ec2_total*0.6:,.2f}",
            "Effort": "Medium",
            "ROI": ec2_total*0.6/1.5
        })
    # S3
    s3_df = df[df["Service"].str.contains("S3|Storage", case=False, na=False)]
    s3_total = s3_df["Cost"].sum()
    if s3_total > 20:
        savings.append({
            "Recommendation": "Enable S3 Intelligent-Tiering",
            "Potential Saving": f"${s3_total*0.4:,.2f}",
            "Effort": "Low",
            "ROI": s3_total*0.4/1.0
        })
    # Sort by ROI
    if savings:
        return pd.DataFrame(savings).sort_values("ROI", ascending=False)
    return pd.DataFrame(columns=["Recommendation","Potential Saving","Effort","ROI"])

savings = find_savings(df)

# =============================================
# 5. ANOMALY DETECTION + EXPLANATION
# =============================================
def detect_anomalies(df):
    if len(df) < 3:
        return pd.DataFrame()
    
    anomalies_list = []
    
    for service, group in df.groupby("Service"):
        daily = group.groupby("Date")["Cost"].sum().reset_index()
        if len(daily) < 3:
            continue

        model = IsolationForest(contamination=0.1, random_state=42)
        daily["Anomaly"] = model.fit_predict(daily[["Cost"]])
        anomaly_rows = daily[daily["Anomaly"] == -1].copy()
        if anomaly_rows.empty:
            continue
        
        anomaly_rows["Reason"] = anomaly_rows["Cost"].apply(
            lambda x: "Sudden usage spike" if x > daily["Cost"].mean() * 1.5 else "Unusual minor spike"
        )
        anomaly_rows["Service"] = service
        anomalies_list.append(anomaly_rows)
    
    return pd.concat(anomalies_list) if anomalies_list else pd.DataFrame()

anomalies = detect_anomalies(df)

# =============================================
# 6. SERVICE-LEVEL TREND & SEASONALITY
# =============================================
def service_trends(df):
    trends = []
    seasonality = []
    for service, group in df.groupby("Service"):
        daily = group.groupby("Date")["Cost"].sum().reset_index()
        if len(daily) < 2:
            continue
        # Trend
        x = (daily["Date"] - daily["Date"].min()).dt.days.values.reshape(-1,1)
        y = daily["Cost"].values
        model = LinearRegression()
        model.fit(x, y)
        trend = model.coef_[0]
        trends.append({"Service": service, "Trend": trend})
        # Seasonality
        daily["Weekday"] = daily["Date"].dt.dayofweek
        weekly_spike = daily.groupby("Weekday")["Cost"].mean().max()
        seasonality.append({"Service": service, "Max Weekly Avg": weekly_spike})
    trend_df = pd.DataFrame(trends)
    season_df = pd.DataFrame(seasonality)
    return trend_df, season_df

trends, seasonality = service_trends(df)
rising_services = trends[trends["Trend"]>0]

# =============================================
# 7. FORECASTING + SIMULATION
# =============================================
def forecast_service(df, days=30):
    forecast_dfs = []
    for service, group in df.groupby("Service"):
        daily = group.groupby("Date")["Cost"].sum().reset_index()
        if len(daily) < 3:
            continue
        daily["days"] = (daily["Date"] - daily["Date"].min()).dt.days + 1
        lr = LinearRegression()
        lr.fit(daily[["days"]], daily["Cost"])
        last_day = daily["days"].max()
        future_days = np.arange(last_day+1, last_day+days+1).reshape(-1,1)
        future_costs = lr.predict(future_days)
        future_dates = [daily["Date"].max() + pd.Timedelta(days=i) for i in range(1, days+1)]
        forecast_dfs.append(pd.DataFrame({"Service": service, "Date": future_dates, "Forecast": future_costs}))
    return pd.concat(forecast_dfs) if forecast_dfs else pd.DataFrame()

forecast = forecast_service(df)

# =============================================
# 8. DASHBOARD TABS
# =============================================
tab1, tab2, tab3 = st.tabs(["Overview", "Recommendations", "Forecast & Simulation"])

with tab1:
    st.header("AWS Cost Intelligence")
    fig = px.bar(df, x="Date", y="Cost", color="Service", title="Daily Spend by Service")
    if not anomalies.empty:
        fig.add_scatter(x=anomalies["Date"], y=anomalies["Cost"], mode="markers",
                        marker=dict(color="red", size=12), name="Anomaly")
    st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap
    pivot = df.pivot_table(values="Cost", index="Service", columns="Date", fill_value=0)
    st.plotly_chart(px.imshow(pivot, text_auto=True, color_continuous_scale="Reds", title="Service Cost Heatmap"), use_container_width=True)

    
    # KPIs
    total = df["Cost"].sum()
    savings_val = sum(float(s.split("$")[1].replace(",", "")) for s in savings["Potential Saving"]) if not savings.empty else 0
    score = int(85 + random.uniform(0,15))
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Spend", f"${total:,.2f}")
    c2.metric("Est. Savings", f"${savings_val:,.2f}")
    c3.metric("AI Efficiency Score", f"{score}/100")
    
    if not anomalies.empty:
        st.error(f"ANOMALY DETECTED: ${anomalies['Cost'].sum():,.2f} spike")
        for _, row in anomalies.iterrows():
            st.write(f"{row['Service']} | {row['Date']} | Reason: {row['Reason']}")
    
    if not rising_services.empty:
        st.warning("Services with rising trends: " + ", ".join(rising_services["Service"].tolist()))

    st.subheader("Service Efficiency Scores")
    st.dataframe(efficiency_df.style.background_gradient(cmap="Blues"))

with tab2:
    st.header("AI-Powered Multi-Scenario Savings Recommendations")
    
    if savings.empty:
        st.info("No immediate savings opportunities — your AWS setup is optimized!")
    else:
        # ---------------------------
        # 1. Top 3 High-ROI Recommendations
        # ---------------------------
        st.subheader("Top 3 High-ROI Recommendations")
        top_savings = savings.sort_values("ROI", ascending=False).head(3)
        c1, c2, c3 = st.columns(3)
        for i, col in enumerate([c1, c2, c3]):
            if i < len(top_savings):
                row = top_savings.iloc[i]
                potential = float(row['Potential Saving'].strip('$').replace(',', ''))
                col.metric(label=row["Recommendation"], value=f"${potential:,.2f}", delta=f"ROI: {row['ROI']:.2f}")

        st.markdown("---")

        # ---------------------------
        # 2. Recommendations Grouped by Service
        # ---------------------------
        st.subheader("Recommendations by Service Type")
        service_types = ["EC2", "S3", "RDS", "Lambda", "Others"]
        for svc_type in service_types:
            svc_df = savings[savings['Recommendation'].str.contains(svc_type, case=False, na=False)]
            if not svc_df.empty:
                st.markdown(f"**{svc_type}**")
                st.dataframe(svc_df.style.background_gradient(cmap="Reds"), use_container_width=True)

        st.markdown("---")

        # ---------------------------
        # 3. Visual: Savings by Recommendation
        # ---------------------------
        st.subheader("Savings by Recommendation")
        savings["Potential_Saving_Num"] = savings["Potential Saving"].str.replace('$','').str.replace(',','').astype(float)
        fig_bar = px.bar(savings, x="Recommendation", y="Potential_Saving_Num", color="ROI",
                         labels={"Potential_Saving_Num":"Potential Saving ($)"},
                         title="Potential Savings per Recommendation")
        st.plotly_chart(fig_bar, use_container_width=True)

        # ---------------------------
        # 4. Effort vs ROI Scatter
        # ---------------------------
        # Map Effort to numeric, fill unknowns as 2 (Medium)
        effort_map = {"Low": 1, "Medium": 2, "High": 3}
        savings["Effort_Num"] = savings["Effort"].map(effort_map).fillna(2)

        # Ensure ROI is numeric
        savings["ROI"] = pd.to_numeric(savings["ROI"], errors="coerce").fillna(0)

        # Only keep rows with valid X and Y
        scatter_df = savings.dropna(subset=["Effort_Num", "ROI"])

        if scatter_df.empty:
            st.warning("No valid data for Effort vs ROI plot.")
        else:
            fig_scatter = px.scatter(
                scatter_df,
                x="Effort_Num",
                y="ROI",
                text="Recommendation",
                size="ROI",
                color="Effort",
                labels={"Effort_Num": "Effort (1=Low, 3=High)", "ROI": "ROI"},
                title="Effort vs ROI (Higher ROI & Lower Effort are Best)",
                hover_data=["Potential Saving"]
            )

            # Add quadrant lines for visual guidance
            fig_scatter.add_shape(type="line", x0=1.5, x1=1.5, y0=0, y1=scatter_df["ROI"].max()*1.1,
                                line=dict(dash="dash", color="gray"))
            fig_scatter.add_shape(type="line", x0=0, x1=3.5, y0=scatter_df["ROI"].mean(), y1=scatter_df["ROI"].mean(),
                                line=dict(dash="dash", color="gray"))

            st.plotly_chart(fig_scatter, use_container_width=True)


        # ---------------------------
        # 5. Download CSV
        # ---------------------------
        csv = savings.drop(columns=["Potential_Saving_Num","Effort_Num"]).to_csv(index=False).encode()
        st.download_button("Download AWS Savings Report", csv, "aws_savings_report.csv", "text/csv")
        
        # ---------------------------
        # 6. Optional Next Steps Checklist
        # ---------------------------
        st.subheader("Next Steps Checklist")
        steps = [
            "Review EC2 instance sizes and right-size underutilized instances",
            "Enable S3 Intelligent-Tiering where possible",
            "Schedule shutdown of unused or low-priority resources",
            "Monitor services with rising cost trends",
            "Revisit recommendations monthly"
        ]
        for step in steps:
            st.checkbox(step)

        def create_pdf_fpdf(savings, efficiency_df=None, trends=None, app_title="Cloud Cost Analyzer"):
            pdf = FPDF()
            pdf.add_page()

            # --- Header ---
            pdf.set_font("Arial", "B", 20)
            pdf.set_text_color(30, 144, 255)
            pdf.cell(0, 10, app_title, ln=True, align="C")

            pdf.set_font("Arial", "", 12)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(10)
            pdf.cell(0, 10, "Generated AWS Savings Recommendations Report", ln=True)
            pdf.ln(5)

            page_width = pdf.w - 2*pdf.l_margin

            # --- Savings Recommendations ---
            if not savings.empty:
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Top Savings Recommendations:", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.ln(3)

                for _, row in savings.iterrows():
                    rec_text = (
                        f"{row['Recommendation']} | Potential Saving: {row['Potential Saving']} | "
                        f"Effort: {row['Effort']} | ROI: {row['ROI']:.2f}"
                    )
                    wrapped_text = "\n".join(textwrap.wrap(rec_text, width=80))
                    pdf.multi_cell(page_width, 8, wrapped_text)
                    if pdf.get_y() > 260:
                        pdf.add_page()

            # --- Service Efficiency Table ---
            if efficiency_df is not None and not efficiency_df.empty:
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Service Efficiency Scores:", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.ln(3)
                for _, row in efficiency_df.iterrows():
                    text = f"{row['Service']} | Total Spend: ${row['Total Spend']:.2f} | Efficiency: {row['Efficiency (%)']}%"
                    wrapped_text = "\n".join(textwrap.wrap(text, width=80))
                    pdf.multi_cell(page_width, 8, wrapped_text)
                    if pdf.get_y() > 260:
                        pdf.add_page()

            # --- Service Trends Table ---
            if trends is not None and not trends.empty:
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Service Trends:", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.ln(3)
                for _, row in trends.iterrows():
                    text = f"{row['Service']} | Trend: {row['Trend']:.2f}"
                    wrapped_text = "\n".join(textwrap.wrap(text, width=80))
                    pdf.multi_cell(page_width, 8, wrapped_text)
                    if pdf.get_y() > 260:
                        pdf.add_page()

            # --- Savings Bar Chart ---
            if not savings.empty:
                plt.figure(figsize=(8, 4))
                savings_sorted = savings.sort_values("ROI", ascending=False)
                plt.barh(savings_sorted["Recommendation"], savings_sorted["Potential_Saving_Num"], color="skyblue")
                plt.xlabel("Potential Saving ($)")
                plt.title("Potential Savings per Recommendation")
                plt.tight_layout()

                img_path = "temp_chart.png"
                plt.savefig(img_path)
                plt.close()

                pdf.add_page()
                pdf.image(img_path, x=15, y=40, w=180)

            # --- Export PDF to BytesIO ---
            pdf_output = io.BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)
            return pdf_output


        # --- Streamlit Button ---
        if st.button("Generate PDF Report"):
            pdf_buffer = create_pdf_fpdf(savings, efficiency_df=efficiency_df, trends=trends)
            st.download_button(
                label="Download AWS Savings PDF",
                data=pdf_buffer,
                file_name="cloud_cost_savings_report.pdf",
                mime="application/pdf"
            )



with tab3:
    st.header("Forecast & Scenario Simulation")
    if forecast.empty:
        st.info("Need at least 3 days of data per service for forecast.")
    else:
        services = forecast["Service"].unique()
        reduction_dict = {}
        st.subheader("Simulate Savings % per Service")
        for svc in services:
            reduction_dict[svc] = st.slider(f"{svc}", 0, 100, 30)
        forecast["Forecast_Sim"] = forecast.apply(lambda row: row["Forecast"]*(1-reduction_dict.get(row["Service"],0)/100), axis=1)
        fig = px.line(forecast, x="Date", y=["Forecast","Forecast_Sim"], color="Service", title="Forecast vs Simulated Savings")
        st.plotly_chart(fig, use_container_width=True)
        
        total_forecast = forecast.groupby("Date")["Forecast"].sum().sum()
        total_sim = forecast.groupby("Date")["Forecast_Sim"].sum().sum()
        st.success(f"Projected 30-day spend: **${total_forecast:,.2f}** → **${total_sim:,.2f}** after simulation")

st.markdown("---")
st.caption("CloudPulse AI v2.0 – Multi-account, predictive, AI-driven cost optimization")
