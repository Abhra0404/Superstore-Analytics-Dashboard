import sys
import os

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
from src.analysis import calculate_kpis
from src.advanced import rfm_analysis


def draw_vertical_divider(height=430, color="#808080"):
    st.markdown(
        f"<div style='display:flex; justify-content:center;'><div style='border-left: 2px solid {color}; height: {height}px;'></div></div>",
        unsafe_allow_html=True,
    )

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Superstore Analytics",
    page_icon="📊",
    layout="wide"
)

# Streamlit Cloud compatibility: avoid Arrow LargeUtf8 dataframe serialization issues.
try:
    st.set_option("global.dataFrameSerialization", "legacy")
except Exception:
    pass

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    data = pd.read_csv("data/cleaned/cleaned_data.csv")
    data['Order Date'] = pd.to_datetime(data['Order Date'], errors='coerce')
    data['Ship Date'] = pd.to_datetime(data['Ship Date'], errors='coerce')
    data = data.dropna(subset=['Order Date'])
    return data

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🎛 Dashboard Controls")
st.sidebar.markdown("Filter data to explore insights")

region_options = sorted(df['Region'].dropna().unique().tolist())
category_options = sorted(df['Category'].dropna().unique().tolist())

region = st.sidebar.multiselect(
    "🌍 Region",
    options=region_options,
    default=region_options
)

category = st.sidebar.multiselect(
    "🛒 Category",
    options=category_options,
    default=category_options
)

df = df[(df['Region'].isin(region)) & (df['Category'].isin(category))]

# ---------------- HEADER ----------------
st.markdown("""
# 📊 Superstore Analytics Dashboard  
### Turning Data into Business Decisions 💼
""")

st.markdown("---")

# ---------------- KPIs ----------------
kpis = calculate_kpis(df)

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Sales", f"${kpis['total_sales']:,.0f}")
col2.metric("📦 Total Orders", kpis['total_orders'])
col3.metric("💳 Avg Order Value", f"${kpis['avg_order_value']:.2f}")

st.markdown("---")

# ---------------- SALES TREND ----------------
st.subheader("📈 Sales Trend Over Time")

sales_trend = df.groupby('Year')['Sales'].sum().reset_index()

fig = px.line(sales_trend, x='Year', y='Sales', markers=True)
fig.update_layout(template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------- CATEGORY ANALYSIS ----------------
col1, divider_col, col2 = st.columns([1, 0.04, 1])

with col1:
    st.subheader("🛒 Category Performance")

    category_sales = df.groupby('Category')['Sales'].sum().reset_index()

    fig = px.bar(category_sales, x='Category', y='Sales', color='Category')
    fig.update_layout(template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🌍 Regional Performance")

    region_sales = df.groupby('Region')['Sales'].sum().reset_index()

    fig = px.bar(region_sales, x='Region', y='Sales', color='Region')
    fig.update_layout(template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

with divider_col:
    st.write("")
    draw_vertical_divider(height=450)

st.markdown("---")

# ---------------- TOP PRODUCTS ----------------
st.subheader("🏆 Top Performing Products")

top_products = df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)
st.markdown(top_products.to_frame(name='Sales').to_html(classes='dataframe', border=0), unsafe_allow_html=True)

st.markdown("---")

# ---------------- RFM ANALYSIS ----------------
st.subheader("👤 Customer Intelligence (RFM Analysis)")

rfm = rfm_analysis(df)

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)

col1.metric("👥 Total Customers", len(rfm))
col2.metric("🏆 Champions", (rfm['Segment'] == "Champions").sum())
col3.metric("⚠️ At Risk", (rfm['Segment'] == "At Risk").sum())

st.markdown("---")

# ---------------- SEGMENT DISTRIBUTION ----------------
col1, divider_col, col2 = st.columns([1, 0.04, 1])

with col1:
    st.markdown("### 📊 Customer Segment Distribution")

    segment_counts = rfm['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']

    fig = px.pie(
        segment_counts,
        names='Segment',
        values='Count',
        hole=0.5
    )

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- REVENUE BY SEGMENT ----------------
with col2:
    st.markdown("### 💰 Revenue Contribution by Segment")

    merged = df.copy()
    merged['Segment'] = merged['Customer ID'].map(rfm['Segment'])
    merged = merged.dropna(subset=['Segment'])

    segment_revenue = merged.groupby('Segment', as_index=False)['Sales'].sum()

    fig = px.bar(
        segment_revenue,
        x='Segment',
        y='Sales',
        color='Segment'
    )

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

with divider_col:
    st.write("")
    draw_vertical_divider(height=430)

st.markdown("---")

# ---------------- TOP CUSTOMERS ----------------
st.markdown("### 🏆 Top High-Value Customers")

top_customers = rfm.sort_values(by='Monetary', ascending=False).head(10)
st.markdown(top_customers[['Recency', 'Frequency', 'Monetary']].to_html(classes='dataframe', border=0), unsafe_allow_html=True)

# ---------------- INSIGHTS TABLE ----------------
st.subheader("🧠 Key Business Insights")

customer_sales = df.groupby('Customer Name')['Sales'].sum().sort_values(ascending=False)
top_10_contribution = (customer_sales.head(10).sum() / customer_sales.sum()) * 100

top_category = df.groupby('Category')['Sales'].sum().idxmax()
top_region = df.groupby('Region')['Sales'].sum().idxmax()

st.markdown(f"""
**📊 Revenue Insights**
- Strong overall revenue performance with consistent sales volume across the dataset  
- Clear seasonal patterns indicating potential demand cycles  
- Opportunity to optimize operations during peak periods  

**🛒 Product Insights**
- **{top_category}** category is the dominant revenue driver  
- High-performing products contribute disproportionately to total sales  
- Focus areas identified for maximizing revenue growth  

**👤 Customer Insights**
- Top 10 customers contribute **{top_10_contribution:.2f}%** of total revenue  
- Indicates high dependency on a small group of customers  
- Strong opportunity for loyalty programs and retention strategies  

**🌍 Regional Insights**
- **{top_region}** region leads in overall sales performance  
- Regional disparities highlight untapped market opportunities  
- Scope for expansion and targeted marketing initiatives  

**🎯 Strategic Recommendations**
- Invest in high-performing categories to drive revenue growth  
- Reduce dependency on top customers by expanding customer base  
- Focus on underperforming regions to unlock new revenue streams  
- Leverage customer segmentation to improve retention and engagement  
""")
st.markdown("---")
# ---------------- DOWNLOAD ----------------
st.download_button(
    label="📥 Download Cleaned Data",
    data=df.to_csv(index=False),
    file_name="cleaned_data.csv",
    mime="text/csv"
)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("### 👾 Built by Abhra | Data Analytics Project")