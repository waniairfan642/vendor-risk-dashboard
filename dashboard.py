import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Vendor Risk Intelligence Dashboard",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
import os

file_path = "data/vendor_risk_analysis.csv"

if not os.path.exists(file_path):
    st.error(f"Data file not found. Ensure '{file_path}' exists in your GitHub repo.")
    st.stop()

# Use 'sep=None' to automatically detect if your CSV uses commas or semicolons
try:
    full_df = pd.read_csv(file_path, sep=None, engine='python')
    
    # Remove any invisible spaces from column names
    full_df.columns = full_df.columns.str.strip()

    # Create a copy for filtering
    vendor_df = full_df.copy()

    # Force these columns to be numbers so math works
    full_df["Risk_Score"] = pd.to_numeric(full_df["Risk_Score"], errors='coerce')
    full_df["Avg_Defect_Rate"] = pd.to_numeric(full_df["Avg_Defect_Rate"], errors='coerce')

    # Calculate the means
    portfolio_avg_risk = full_df["Risk_Score"].mean()
    avg_defect_rate = full_df["Avg_Defect_Rate"].mean()

except KeyError as e:
    st.error(f"Could not find column: {e}")
    st.write("The columns found in your file are:", full_df.columns.tolist())
    st.stop()
# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.header("Filter Options")

selected_vendor = st.sidebar.selectbox(
    "Select Vendor",
    options=["All"] + sorted(full_df["Supplier"].unique())
)

if selected_vendor != "All":
    vendor_df = full_df[full_df["Supplier"] == selected_vendor]

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.title("Vendor Risk Intelligence Dashboard")
st.caption("Executive Overview of Vendor Performance & Risk Intelligence")

st.divider()

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.subheader("Portfolio Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Vendors", full_df["Supplier"].nunique())
col2.metric("Average Risk Score", round(portfolio_avg_risk, 3))
col3.metric("Avg Cancellation Rate (%)", round(full_df["Cancellation_Rate_%"].mean(), 2))
col4.metric("Avg Defect Rate", round(avg_defect_rate, 3))

st.divider()

# --------------------------------------------------
# 🔥 TOP GRAPH (MAIN)
# --------------------------------------------------
st.subheader("Vendor Risk vs Performance")

fig_scatter = px.scatter(
    full_df,
    x="Avg_Defect_Rate",
    y="Risk_Score",
    size="Cancellation_Rate_%",
    color="Risk_Category",
    text="Supplier",
    hover_name="Supplier",
    color_discrete_map={
        "High Risk": "red",
        "Medium Risk": "orange",
        "Low Risk": "green"
    }
)

fig_scatter.add_hline(y=portfolio_avg_risk, line_dash="dash", line_color="white")
fig_scatter.add_vline(x=avg_defect_rate, line_dash="dash", line_color="white")

fig_scatter.update_traces(textposition='top center')

st.plotly_chart(fig_scatter, use_container_width=True, key="main_scatter")

st.divider()

# --------------------------------------------------
# RISK RANKING
# --------------------------------------------------
st.subheader("Vendor Risk Ranking")

fig_risk = px.bar(
    full_df.sort_values("Risk_Score", ascending=False),
    x="Supplier",
    y="Risk_Score",
    color="Risk_Category",
    color_discrete_map={
        "High Risk": "red",
        "Medium Risk": "orange",
        "Low Risk": "green"
    }
)

fig_risk.add_hline(y=portfolio_avg_risk, line_dash="dash", line_color="white")

st.plotly_chart(fig_risk, use_container_width=True, key="risk_ranking")

st.divider()

# --------------------------------------------------
# TOP 5
# --------------------------------------------------
st.subheader("Top 5 Vendors by Risk Score")

top5 = full_df.nlargest(5, "Risk_Score")

fig_top5 = px.bar(
    top5,
    x="Supplier",
    y="Risk_Score",
    color="Risk_Score",
    color_continuous_scale="reds"
)

st.plotly_chart(fig_top5, use_container_width=True, key="top5")

st.divider()

# --------------------------------------------------
# DISTRIBUTION
# --------------------------------------------------
st.subheader("Risk Score Distribution")

fig_dist = px.histogram(
    full_df,
    x="Risk_Score",
    nbins=15,
    color="Risk_Category"
)

st.plotly_chart(fig_dist, use_container_width=True, key="distribution")

st.divider()

# --------------------------------------------------
# DONUT CHART
# --------------------------------------------------
st.subheader("Risk Category Distribution")

fig_pie = px.pie(
    full_df,
    names="Risk_Category",
    hole=0.4,
    color="Risk_Category",
    color_discrete_map={
        "High Risk": "red",
        "Medium Risk": "orange",
        "Low Risk": "green"
    }
)

st.plotly_chart(fig_pie, use_container_width=True, key="pie")

st.divider()

# --------------------------------------------------
# HEATMAP
# --------------------------------------------------
st.subheader("Correlation Analysis")

corr = full_df[[
    "Risk_Score",
    "Cancellation_Rate_%",
    "Avg_Defect_Rate",
    "Compliance_Rate"
]].corr()

fig_heatmap = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu")

st.plotly_chart(fig_heatmap, use_container_width=True, key="heatmap")

st.divider()

# --------------------------------------------------
# CANCELLATION VS DEFECT (FIXED)
# --------------------------------------------------
st.subheader("Cancellation vs Defect Rate")

fig_cd = px.scatter(
    full_df,
    x="Cancellation_Rate_%",
    y="Avg_Defect_Rate",
    color="Risk_Category",
    text="Supplier"
)

fig_cd.update_traces(textposition="top center")

st.plotly_chart(fig_cd, use_container_width=True, key="cancel_vs_defect")

st.divider()

# --------------------------------------------------
# COMPLIANCE VS RISK
# --------------------------------------------------
st.subheader("Compliance vs Risk")

fig_comp = px.scatter(
    full_df,
    x="Compliance_Rate",
    y="Risk_Score",
    color="Risk_Category",
    text="Supplier"
)

fig_comp.update_traces(textposition="top center")

st.plotly_chart(fig_comp, use_container_width=True, key="compliance_vs_risk")

st.divider()

# --------------------------------------------------
# NORMALIZED COMPARISON
# --------------------------------------------------
st.subheader("Normalized Performance Comparison")

metrics = [
    "Norm_Cancellation",
    "Norm_Defect",
    "Norm_Delay",
    "Norm_Compliance_Risk"
]

if selected_vendor != "All":
    fig_compare = px.bar(
        vendor_df,
        x="Supplier",
        y=metrics,
        barmode="group"
    )
    st.plotly_chart(fig_compare, use_container_width=True, key="normalized")
else:
    st.info("Select a vendor to view comparison")

st.divider()

# --------------------------------------------------
# INSIGHT PANEL
# --------------------------------------------------
st.subheader("Strategic Insight")

highest = full_df.sort_values("Risk_Score", ascending=False).iloc[0]

st.warning(f"""
Highest Risk Vendor: {highest['Supplier']}

Risk Score: {round(highest['Risk_Score'],3)}
Cancellation Rate: {round(highest['Cancellation_Rate_%'],2)}%
Defect Rate: {round(highest['Avg_Defect_Rate'],3)}
Compliance Rate: {round(highest['Compliance_Rate'],2)}
""")

st.divider()

# --------------------------------------------------
# TABLE
# --------------------------------------------------
st.subheader("Detailed Data")

st.dataframe(full_df.sort_values("Risk_Score", ascending=False))
#streamlit run python/dashboard.py
