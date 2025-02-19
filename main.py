import streamlit as st
import pandas as pd
import requests
from io import StringIO

def load_price_change_data(url):
    df = pd.read_csv(url)
    df = df[["SKU", "Price Increase due to stock location or Low stock"]]
    df["SKU"] = df["SKU"].astype(str)
    df_last_occurrences = df.drop_duplicates(subset="SKU", keep="last")
    df_true_values = df_last_occurrences[
        df_last_occurrences["Price Increase due to stock location or Low stock"] == True]
    return df_true_values

def load_free_stock_report(url):
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to download stock report data.")
        return None
    lookup_df = pd.read_csv(StringIO(response.text), skiprows=3)
    lookup_df.iloc[:, 0] = lookup_df.iloc[:, 0].astype(str)
    selected_columns = [0, 5, 6, 12, 13, 19, 20]
    extra_data_df = lookup_df.iloc[:, selected_columns]
    extra_data_df.columns = ['Sku code','SKU Description', 'UK Stock', 'UK Cover', 'NL Stock', 'NL Cover', 'MG Stock', 'MG Cover']
    return extra_data_df

def process_data(price_change_url, stock_report_url, output_file):
    df_true_values = load_price_change_data(price_change_url)
    extra_data_df = load_free_stock_report(stock_report_url)
    if df_true_values is not None and extra_data_df is not None:
        df_true_values = df_true_values.set_index('SKU').join(extra_data_df.set_index('Sku code'), how='left')
        df_true_values.to_csv(output_file)
        return df_true_values
    return None

st.title("UK & EU Price Change Processing")

option = st.selectbox("Select Region", ["UK", "EU"])

price_change_urls = {
    "UK": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRQdch8ifiMx_U_itOI8x2OOEUwc0gj_NGgGO6gDvbV88UoTOqqA_Lick99Ka8jYKwF18itR14stkFE/pub?gid=0&single=true&output=csv",
    "EU": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRQdch8ifiMx_U_itOI8x2OOEUwc0gj_NGgGO6gDvbV88UoTOqqA_Lick99Ka8jYKwF18itR14stkFE/pub?gid=1300694374&single=true&output=csv"
}

stock_report_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTMRiRm7_GGUY1gmeGXQc3q85qNUvry1OKXWWYkPVQIdTFQTXi7LUS1IgVjrDVnmsLDvL8M12aWYqQ4/pub?output=csv"
output_files = {"UK": "data_UK.csv", "EU": "data_EU.csv"}

if st.button("Run Script"):
    with st.spinner("Processing data..."):
        df_result = process_data(price_change_urls[option], stock_report_url, output_files[option])
        if df_result is not None:
            st.success("Processing completed successfully!")
            st.dataframe(df_result.head())
        else:
            st.error("Processing failed.")
