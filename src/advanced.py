import pandas as pd


def rfm_analysis(df):
    df = df.copy()
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    df = df.dropna(subset=['Order Date'])

    if df.empty:
        raise ValueError("No valid 'Order Date' values available for RFM analysis.")

    snapshot_date = df['Order Date'].max() + pd.Timedelta(days=1)

    rfm = df.groupby('Customer ID').agg({
        'Order Date': lambda x: (snapshot_date - x.max()).days,
        'Order ID': 'nunique',
        'Sales': 'sum'
    })

    rfm.columns = ['Recency', 'Frequency', 'Monetary']

    # Scoring
    rfm['R_score'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1])
    rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
    rfm['M_score'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5])

    # Segment
    def segment(row):
        if row['R_score'] >= 4 and row['F_score'] >= 4:
            return "Champions"
        elif row['R_score'] >= 3:
            return "Loyal Customers"
        elif row['R_score'] <= 2:
            return "At Risk"
        else:
            return "Others"

    rfm['Segment'] = rfm.apply(segment, axis=1)

    return rfm


def monthly_trend(df):
    return df.groupby('Month Name')['Sales'].sum()


def region_category_analysis(df):
    return df.groupby(['Region','Category'])['Sales'].sum()