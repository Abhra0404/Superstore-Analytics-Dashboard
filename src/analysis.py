def calculate_kpis(df):
    total_sales = df['Sales'].sum()
    total_orders = df['Order ID'].nunique()
    avg_order_value = total_sales / total_orders

    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "avg_order_value": avg_order_value
    }


def category_analysis(df):
    return df.groupby('Category')['Sales'].sum().sort_values(ascending=False)


def subcategory_analysis(df):
    return df.groupby('Sub-Category')['Sales'].sum().sort_values(ascending=False)


def regional_sales(df):
    return df.groupby('Region')['Sales'].sum().sort_values(ascending=False)


def customer_analysis(df):
    return df.groupby('Customer Name')['Sales'].sum().sort_values(ascending=False)