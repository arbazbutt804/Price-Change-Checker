import streamlit as st
import pandas as pd
import requests
from io import StringIO

def load_price_change_data(url):
    df = pd.read_csv(url)
    df = df[["SKU", "Price Increase due to stock location or Low stock"]]
    df["SKU"] = df["SKU"].astype(str)
    df_last_occurrences = df.drop_duplicates(subset="SKU", keep="last")
    df_last_occurrences["SKU"] = df_last_occurrences["SKU"].astype(str).str.strip()  # Strip whitespace
    df_last_occurrences = df_last_occurrences[df_last_occurrences["SKU"].str.len() > 0]  # Remove empty SKUs
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
    selected_columns = [0, 1 , 5, 6, 12, 13, 19, 20]
    extra_data_df = lookup_df.iloc[:, selected_columns]
    extra_data_df.columns = ['Sku code','SKU Description', 'UK Stock', 'UK Cover', 'NL Stock', 'NL Cover', 'MG Stock', 'MG Cover']
    return extra_data_df

def process_data(price_change_url, stock_report_url, output_file):
    df_true_values = load_price_change_data(price_change_url)
    extra_data_df = load_free_stock_report(stock_report_url)
    if df_true_values is not None and extra_data_df is not None:
        df_true_values = df_true_values.set_index('SKU').join(extra_data_df.set_index('Sku code'), how='left').reset_index()
    return df_true_values

# Function to convert dataframe to CSV for download
def convert_df_to_csv(df):
    csv = df.to_csv(index=False)
    return csv

# Set the page configuration
st.set_page_config(page_title="UK & EU Price Change Processing", layout="centered")

# Using HTML and CSS to center the title
st.markdown("""
    <style>
        .title {
            text-align: center;
            font-size: 2.5em;
            color: #2F4F4F;
        }
        .container {
            padding: 20px;
        }
        .download-btn {
            margin-top: 20px;
            text-align: center;
        }
    </style>
    <h1 class="title">📊 Price Update & Stock Management</h1>
""", unsafe_allow_html=True)

# Using HTML to style the selectbox header
st.markdown("""
    <style>
        .selectbox-container {
            text-align: center;
            margin-top: 30px;
            font-size: 18px;
        }
        .stSelectbox > div > div > input {
            height: 40px;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)


# Custom-styled Selectbox
with st.container():
    st.markdown('<div class="selectbox-container"><label>Select Region:</label></div>', unsafe_allow_html=True)
    option = st.selectbox(
        ["UK", "EU"],
        index=0,
        key="region_select",
        help="Choose the region to process price changes"
    )

price_change_urls = {
    "UK": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRQdch8ifiMx_U_itOI8x2OOEUwc0gj_NGgGO6gDvbV88UoTOqqA_Lick99Ka8jYKwF18itR14stkFE/pub?gid=0&single=true&output=csv",
    "EU": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRQdch8ifiMx_U_itOI8x2OOEUwc0gj_NGgGO6gDvbV88UoTOqqA_Lick99Ka8jYKwF18itR14stkFE/pub?gid=1300694374&single=true&output=csv"
}

stock_report_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTMRiRm7_GGUY1gmeGXQc3q85qNUvry1OKXWWYkPVQIdTFQTXi7LUS1IgVjrDVnmsLDvL8M12aWYqQ4/pub?output=csv"
output_files = {"UK": "data_UK.csv", "EU": "data_EU.csv"}
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔍 Process Data", use_container_width=True):
        with st.spinner("Processing data"):
            df_result = process_data(price_change_urls[option], stock_report_url, output_files[option])
            if df_result is not None:
                # Convert the processed DataFrame to CSV
                csv_data = convert_df_to_csv(df_result)
                #st.success("Processing completed successfully!")
                st.download_button(
                    label="Download Processed Data",
                    data=csv_data,
                    file_name=f"{output_files[option]}",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.error("Processing failed.")