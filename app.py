

# ==========================================
# SALES ANALYTICS INTERACTIVE DASHBOARD
# Python + Pandas + Matplotlib + Seaborn
# + Plotly + Streamlit
# ==========================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# 1. PAGE CONFIGURATION

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# 2. CUSTOM CSS

st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
h1 {
    color: #17365d;
}
h2, h3 {
    color: #23476a;
}
[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# 3. DASHBOARD TITLE

st.title("📊 Sales Analytics Dashboard")

st.write(
    "Welcome! Analyze sales, revenue, products "
    "and regional business performance."
)

st.divider()

# 4. LOAD DATASET

@st.cache_data
def load_data():
    data = pd.read_csv("sales_data.csv")
    data["Date"] = pd.to_datetime(data["Date"])
    return data

try:
    df = load_data()
except FileNotFoundError:
    st.error("sales_data.csv file not found.")
    st.stop()
except Exception as e:
    st.error(f"Unable to load data: {e}")
    st.stop()

# 5. SIDEBAR FILTERS

st.sidebar.title("🔍 Dashboard Filters")

regions = st.sidebar.multiselect(
    "Select Region",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

categories = st.sidebar.multiselect(
    "Select Category",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

payments = st.sidebar.multiselect(
    "Select Payment Method",
    options=sorted(df["Payment"].unique()),
    default=sorted(df["Payment"].unique())
)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# 6. APPLY FILTERS

if len(date_range) != 2:
    st.warning("Please select a start date and end date.")
    st.stop()

start_date, end_date = date_range

filtered_df = df[
    (df["Region"].isin(regions)) &
    (df["Category"].isin(categories)) &
    (df["Payment"].isin(payments)) &
    (df["Date"].dt.date >= start_date) &
    (df["Date"].dt.date <= end_date)
]

if filtered_df.empty:
    st.warning("No sales data found for selected filters.")
    st.stop()

# 7. CALCULATE BUSINESS METRICS

total_revenue = filtered_df["Revenue"].sum()

total_orders = filtered_df["Order_ID"].nunique()

total_quantity = filtered_df["Quantity"].sum()

average_order = total_revenue / total_orders

# 8. DISPLAY KPI CARDS

st.subheader("📌 Business Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Revenue",
    f"₹{total_revenue:,.0f}"
)

col2.metric(
    "Total Orders",
    f"{total_orders:,}"
)

col3.metric(
    "Products Sold",
    f"{total_quantity:,}"
)

col4.metric(
    "Average Order Value",
    f"₹{average_order:,.2f}"
)

st.divider()

# 9. MONTHLY SALES - MATPLOTLIB

st.subheader("📈 Monthly Revenue Analysis")

monthly_sales = (
    filtered_df
    .groupby(filtered_df["Date"].dt.to_period("M"))["Revenue"]
    .sum()
)

monthly_sales.index = monthly_sales.index.astype(str)

fig, ax = plt.subplots(figsize=(12, 4))

ax.plot(
    monthly_sales.index,
    monthly_sales.values,
    marker="o",
    linewidth=2
)

ax.set_title("Monthly Revenue")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (₹)")
ax.grid(True, alpha=0.3)

plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.divider()

# 10. CATEGORY SALES - SEABORN

st.subheader("📊 Category-wise Revenue")

category_sales = (
    filtered_df
    .groupby("Category", as_index=False)["Revenue"]
    .sum()
)

fig, ax = plt.subplots(figsize=(10, 4))

sns.barplot(
    data=category_sales,
    x="Category",
    y="Revenue",
    ax=ax
)

ax.set_title("Revenue by Category")
ax.set_xlabel("Category")
ax.set_ylabel("Revenue (₹)")

plt.xticks(rotation=20)
plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.divider()

# 11. PRODUCT SALES - PLOTLY

st.subheader("🛍️ Product-wise Sales")

product_sales = (
    filtered_df
    .groupby("Product", as_index=False)["Revenue"]
    .sum()
)

fig = px.bar(
    product_sales,
    x="Product",
    y="Revenue",
    color="Product",
    title="Product Revenue Comparison",
    text_auto=True
)

fig.update_layout(
    xaxis_title="Product",
    yaxis_title="Revenue (₹)"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# 12. REGIONAL SALES - PLOTLY

st.subheader("🌍 Regional Sales Distribution")

region_sales = (
    filtered_df
    .groupby("Region", as_index=False)["Revenue"]
    .sum()
)

fig = px.pie(
    region_sales,
    names="Region",
    values="Revenue",
    title="Revenue by Region",
    hole=0.4
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# 13. PAYMENT METHOD ANALYSIS

st.subheader("💳 Payment Method Analysis")

payment_sales = (
    filtered_df
    .groupby("Payment", as_index=False)["Revenue"]
    .sum()
)

fig = px.bar(
    payment_sales,
    x="Payment",
    y="Revenue",
    color="Payment",
    title="Sales by Payment Method"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# 14. TOP 5 PRODUCTS

st.subheader("🏆 Top Selling Products")

top_products = (
    filtered_df
    .groupby("Product")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

st.dataframe(
    top_products,
    use_container_width=True,
    hide_index=True
)

st.divider()

# 15. DISPLAY SALES DATA

st.subheader("📋 Complete Sales Records")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# 16. DOWNLOAD REPORT

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Sales Report",
    data=csv_data,
    file_name="sales_report.csv",
    mime="text/csv"
)

# 17. FOOTER

st.divider()

st.caption(
    "Sales Analytics Dashboard | Developed using Python "
    "Pandas, Matplotlib, Seaborn, Plotly and Streamlit"
)

st.success("Dashboard loaded successfully!")
