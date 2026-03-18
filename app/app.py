import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
from src.analysis import calculate_kpis
from src.advanced import rfm_analysis
from src.preprocess import clean_data

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Superstore Intelligence",
    page_icon="📊",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/cleaned/cleaned_data.csv")

    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')

    if 'Year' not in df.columns:
        df['Year'] = df['Order Date'].dt.year

    df = df.dropna(subset=['Sales'])

    if df.empty:
        raw = pd.read_csv("data/raw/superstore.csv")
        df = clean_data(raw)

    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🎛 Controls")

region = st.sidebar.multiselect(
    "🌍 Region",
    df['Region'].unique(),
    default=list(df['Region'].unique())
)

category = st.sidebar.multiselect(
    "🛒 Category",
    df['Category'].unique(),
    default=list(df['Category'].unique())
)

filtered_df = df.copy()

if region:
    filtered_df = filtered_df[filtered_df['Region'].isin(region)]
if category:
    filtered_df = filtered_df[filtered_df['Category'].isin(category)]

if filtered_df.empty:
    st.warning("No data for selected filters — showing full dataset")
    filtered_df = df.copy()

# ---------------- HEADER ----------------
st.markdown("""
# 📊 Superstore Intelligence Dashboard  
### Real-time Business Insights & Decision Engine 💼
""")

# ---------------- KPI STRIP ----------------
kpis = calculate_kpis(filtered_df)

c1, c2, c3 = st.columns(3)

c1.metric("💰 Revenue", f"${kpis['total_sales']:,.0f}")
c2.metric("📦 Orders", kpis['total_orders'])
c3.metric("💳 Avg Order Value", f"${kpis['avg_order_value']:.2f}")

st.markdown("---")

# ---------------- MAIN GRID ----------------
col1, col2 = st.columns(2)

# -------- SALES TREND --------
with col1:
    st.markdown("### 📈 Revenue Trend")

    trend = (
        filtered_df.groupby('Year')['Sales']
        .sum()
        .reset_index()
        .sort_values('Year')
    )

    fig = px.line(trend, x='Year', y='Sales', markers=True)
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# -------- CATEGORY --------
with col2:
    st.markdown("### 🛒 Category Performance")

    cat = (
        filtered_df.groupby('Category')['Sales']
        .sum()
        .reset_index()
    )

    fig = px.bar(cat, x='Category', y='Sales', color='Category')
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------- SECOND ROW ----------------
col1, col2 = st.columns(2)

# -------- REGION --------
with col1:
    st.markdown("### 🌍 Regional Distribution")

    reg = (
        filtered_df.groupby('Region')['Sales']
        .sum()
        .reset_index()
    )

    fig = px.bar(reg, x='Region', y='Sales', color='Region')
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# -------- RFM PIE --------
with col2:
    st.markdown("### 👤 Customer Segments")

    rfm = rfm_analysis(filtered_df)

    seg = rfm['Segment'].value_counts().reset_index()
    seg.columns = ['Segment', 'Count']

    fig = px.pie(seg, names='Segment', values='Count', hole=0.5)
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------- RFM DETAIL ----------------
st.markdown("### 🧠 Customer Intelligence")

c1, c2, c3 = st.columns(3)

c1.metric("👥 Customers", len(rfm))
c2.metric("🏆 Champions", (rfm['Segment']=="Champions").sum())
c3.metric("⚠️ At Risk", (rfm['Segment']=="At Risk").sum())

# Revenue by segment
merged = filtered_df.copy()
merged['Segment'] = merged['Customer ID'].map(rfm['Segment'])

rev = merged.groupby('Segment')['Sales'].sum().reset_index()

fig = px.bar(rev, x='Segment', y='Sales', color='Segment')
fig.update_layout(template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------- TOP PRODUCTS ----------------
st.markdown("### 🏆 Top Products")

top_products = (
    filtered_df.groupby('Product Name')['Sales']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.dataframe(top_products, use_container_width=True)

st.markdown("---")

# ---------------- INSIGHTS ----------------
st.markdown("### 🧠 Strategic Insights")

customer_sales = filtered_df.groupby('Customer Name')['Sales'].sum().sort_values(ascending=False)
top_10 = (customer_sales.head(10).sum()/customer_sales.sum())*100

top_cat = filtered_df.groupby('Category')['Sales'].sum().idxmax()
top_reg = filtered_df.groupby('Region')['Sales'].sum().idxmax()

st.markdown(f"""
- 📊 Strong revenue performance across dataset  
- 🛒 **{top_cat}** drives majority of sales  
- 👤 Top 10 customers contribute **{top_10:.2f}%** revenue  
- 🌍 **{top_reg}** region dominates performance  
- 🎯 Expansion + retention = biggest growth lever  
""")

st.markdown("---")

# ---------------- DOWNLOAD ----------------
st.download_button(
    "📥 Download Data",
    filtered_df.to_csv(index=False),
    "data.csv"
)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("### 🚀 Built by Abhra | Business Intelligence Project")