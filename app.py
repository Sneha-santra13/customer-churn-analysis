import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Premium Dashboard", layout="wide")

# -------------------------
# STYLE
# -------------------------
st.markdown("""
<style>
.main {
    background-color: #f8fafc;
}
h1, h2, h3 {
    color: #111827;
}
.stMetric {
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: white;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
st.markdown("# 🚀 Customer Churn Premium Dashboard")
st.markdown("### Power BI Style • Interactive • Clean")
st.markdown("---")

# -------------------------
# FILE UPLOAD
# -------------------------
file = st.file_uploader("Upload CSV File", type=["csv"])

# -------------------------
# NORMALIZE COLUMNS
# -------------------------
def normalize(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

# -------------------------
# MAIN
# -------------------------
if file is not None:

    df = pd.read_csv(file)

    if df.empty:
        st.error("Dataset is empty")
        st.stop()

    df = normalize(df)

    # Detect columns safely
    geo = "geography" if "geography" in df.columns else None
    gender = "gender" if "gender" in df.columns else None
    churn = "exited" if "exited" in df.columns else None
    age = "age" if "age" in df.columns else None
    balance = "balance" if "balance" in df.columns else None

    # -------------------------
    # SIDEBAR FILTERS
    # -------------------------
    st.sidebar.header("🔍 Filters")

    filtered = df.copy()

    if geo:
        geo_opt = sorted(df[geo].dropna().astype(str).unique())
        sel_geo = st.sidebar.multiselect("Geography", geo_opt, default=geo_opt)
        if sel_geo:
            filtered = filtered[filtered[geo].astype(str).isin(sel_geo)]

    if gender:
        gender_opt = sorted(df[gender].dropna().astype(str).unique())
        sel_gender = st.sidebar.multiselect("Gender", gender_opt, default=gender_opt)
        if sel_gender:
            filtered = filtered[filtered[gender].astype(str).isin(sel_gender)]

    if filtered.empty:
        st.warning("No data after filtering. Showing full dataset.")
        filtered = df.copy()

    # -------------------------
    # KPIs
    # -------------------------
    st.markdown("## 📊 Key Metrics")

    total = len(filtered)
    churn_rate = filtered[churn].mean()*100 if churn else 0
    avg_balance = filtered[balance].mean() if balance else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("👥 Customers", total)
    c2.metric("📉 Churn %", f"{churn_rate:.2f}")
    c3.metric("💰 Avg Balance", f"{avg_balance:.0f}")

    st.markdown("---")

    # -------------------------
    # CHARTS
    # -------------------------
    st.markdown("## 📈 Insights")

    col1, col2 = st.columns(2)

    # Geography
    with col1:
        if geo:
            geo_data = filtered.groupby(geo).size().reset_index(name="Count")
            fig = px.bar(geo_data, x=geo, y="Count", color=geo, title="Customers by Geography")
            st.plotly_chart(fig, use_container_width=True)

    # Gender
    with col2:
        if gender:
            gender_data = filtered.groupby(gender).size().reset_index(name="Count")
            fig = px.pie(gender_data, names=gender, values="Count", title="Gender Distribution")
            st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # CHURN DISTRIBUTION
    # -------------------------
    if churn:
        churn_data = filtered[churn].value_counts().reset_index()
        churn_data.columns = ["Churn", "Count"]

        fig = px.pie(churn_data, names="Churn", values="Count", title="Churn Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # AGE GROUP (POWER BI STYLE)
    # -------------------------
    if age and churn:
        st.markdown("### 📊 Churn by Age Group")

        temp = filtered.copy()

        temp["AgeGroup"] = pd.cut(
            temp[age],
            bins=[18,30,45,60,100],
            labels=["18-30","30-45","45-60","60+"]
        )

        age_data = temp.groupby("AgeGroup")[churn].mean().reset_index()

        fig = px.bar(
            age_data,
            x="AgeGroup",
            y=churn,
            color="AgeGroup",
            text_auto=True,
            title="Churn Rate by Age Group"
        )

        st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # HIGH VALUE
    # -------------------------
    if balance and churn:
        st.markdown("## 💰 High Value Customers")

        median = filtered[balance].median()
        hv = filtered[filtered[balance] > median]

        if not hv.empty:
            hv_churn = hv[churn].mean()*100
            st.metric("High Value Churn %", f"{hv_churn:.2f}")

    # -------------------------
    # DATA VIEW
    # -------------------------
    with st.expander("🔍 View Data"):
        st.dataframe(filtered.head())

else:
    st.info("Upload CSV file to start")