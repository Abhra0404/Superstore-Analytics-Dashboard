import sys
import os

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
from src.analysis import calculate_kpis
from src.advanced import rfm_analysis
from src.preprocess import clean_data

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Superstore Analytics",
    page_icon="📊",
    layout="wide"
)

# Fix Streamlit dataframe serialization issue
try:
    st.set_option("global.dataFrameSerialization", "legacy")
except Exception:
    pass

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    data = pd.read_csv("data/cleaned/cleaned_data.csv")

    # Fix datetime safely
    data['Order Date'] = pd.to_datetime(data['Order Date'], errors='coerce')
    data['Ship Date'] = pd.to_datetime(data['Ship Date'], errors='coerce')

    # Fix Sales column
    if 'Sales' in data.columns:
        data['Sales'] = pd.to_numeric(
            data['Sales']
            .astype(str)
            .str.replace('$', '', regex=False)
            .str.replace(',', '', regex=False)
            .str.strip(),
            errors='coerce'
        )

    # Only create Year if missing
    if 'Year' not in data.columns:
        data['Year'] = data['Order Date'].dt.year

    # Drop only critical nulls
    data = data.dropna(subset=['Sales'])

    # Fallback if dataset broken
    if data.empty or data['Sales'].sum() <= 0:
        raw_data = pd.read_csv("data/raw/superstore.csv")
        data = clean_data(raw_data)

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

# Safe filtering
filtered_df = df.copy()

if region:
    filtered_df = filtered_df[filtered_df['Region'].isin(region)]

if category:
    filtered_df = filtered_df[filtered_df['Category'].isin(category)]

if filtered_df.empty:
    st.warning("No data for selected filters. Showing full dataset.")
    filtered_df = df.copy()

# ---------------- HEADER ----------------
st.markdown("""
# 📊 Superstore Analytics Dashboard  
### Turning Data into Business Decisions 💼
""")

st.markdown("---")

# ---------------- KPIs ----------------
kpis = calculate_kpis(filtered_df)

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Sales", f"${kpis['total_sales']:,.0f}")
col2.metric("📦 Total Orders", kpis['total_orders'])
col3.metric("💳 Avg Order Value", f"${kpis['avg_order_value']:.2f}")

st.markdown("---")

# ---------------- SALES TREND ----------------
st.subheader("📈 Sales Trend Over Time")

sales_trend = (
    filtered_df.groupby('Year')['Sales']
    .sum()
    .reset_index()
    .dropna()
    .sort_values('Year')
)

fig = px.line(sales_trend, x='Year', y='Sales', markers=True)
fig.update_layout(template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------- CATEGORY & REGION ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛒 Category Performance")

    category_sales = (
        filtered_df.groupby('Category')['Sales']
        .sum()
        .reset_index()
    )

    fig = px.bar(category_sales, x='Category', y='Sales', color='Category')
    fig.update_layout(template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🌍 Regional Performance")

    region_sales = (
        filtered_df.groupby('Region')['Sales']
        .sum()
        .reset_index()
    )

    fig = px.bar(region_sales, x='Region', y='Sales', color='Region')
    fig.update_layout(template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------- TOP PRODUCTS ----------------
st.subheader("🏆 Top Performing Products")

top_products = (
    filtered_df.groupby('Product Name')['Sales']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.dataframe(top_products, use_container_width=True)

st.markdown("---")

# ---------------- RFM ----------------
st.subheader("👤 Customer Intelligence (RFM Analysis)")

rfm = rfm_analysis(filtered_df)

col1, col2, col3 = st.columns(3)

col1.metric("👥 Total Customers", len(rfm))
col2.metric("🏆 Champions", (rfm['Segment'] == "Champions").sum())
col3.metric("⚠️ At Risk", (rfm['Segment'] == "At Risk").sum())

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Segment Distribution")

    segment_counts = rfm['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']

    fig = px.pie(segment_counts, names='Segment', values='Count', hole=0.5)
    fig.update_layout(template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 💰 Revenue by Segment")

    merged = filtered_df.copy()
    merged['Segment'] = merged['Customer ID'].map(rfm['Segment'])
    merged = merged.dropna(subset=['Segment'])

    segment_revenue = (
        merged.groupby('Segment')['Sales']
        .sum()
        .reset_index()
    )

    fig = px.bar(segment_revenue, x='Segment', y='Sales', color='Segment')
    fig.update_layout(template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------- INSIGHTS ----------------
st.subheader("🧠 Key Business Insights")

customer_sales = filtered_df.groupby('Customer Name')['Sales'].sum().sort_values(ascending=False)
top_10_contribution = (customer_sales.head(10).sum() / customer_sales.sum()) * 100

top_category = filtered_df.groupby('Category')['Sales'].sum().idxmax()
top_region = filtered_df.groupby('Region')['Sales'].sum().idxmax()

st.markdown(f"""
- 📊 Strong revenue performance with consistent sales trends  
- 🛒 **{top_category}** category drives maximum revenue  
- 👤 Top 10 customers contribute **{top_10_contribution:.2f}%** of total revenue  
- 🌍 **{top_region}** region leads in sales performance  
- 🎯 Opportunity to expand in underperforming regions and reduce customer concentration risk  
""")

st.markdown("---")

# ---------------- DOWNLOAD ----------------
st.download_button(
    label="📥 Download Data",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv"
)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("### 👾 Built by Abhra | Data Analytics Project")