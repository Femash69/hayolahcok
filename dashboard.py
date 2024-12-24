pip install streamlit
pip install pandas
pip install numpy
pip install matplotlib
pip isntall seaborn
pip install os
pip install gdown
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os
import gdown

st.title("Analisis Data dalam Bidang E-commerce")

st.header("Proyek Analisis Data dengan Python")
st.subheader("Dalam dashboard ini dibahas dua pertanyaan terkait e-commerce, yakni:")
st.markdown("""
1. **Bagaimana sebaran pembelian pelanggan dan bagaimana pelanggan dapat dikelompokkan berdasarkan jumlah pengeluarannya?**
2. **Di negara bagian mana penjualan memiliki potensi yang menjanjikan dan pantas untuk diperhatikan?**

Selain itu, dibahas juga mengenai tren pembelian konsumen melalui e-commerce dalam kurun waktu 2 tahun. 
Gunakan panel di sebelah kiri untuk memilih visualisasi yang ingin Anda lihat.
""")


output_dir = "./datasets"
os.makedirs(output_dir, exist_ok=True)

file_ids = {
    "sellers_dataset.csv": "1PVqsj2_--k9HBV7oPbF4i4uPl273fWUN",
    "product_category.csv": "1jzM-zFzGcUTbwNmVIMQOBS9icOtah-WS",
    "customers_dataset.csv": "1TVcgRTVm8AJ09_gT7UoTeint3GqxxX3F",
    "geolocation_dataset.csv": "1VDgmPctoYutFwXEHgJ_2TDWQfrF2YtSU",
    "orders_dataset.csv": "1neYI5QTFG7LYyM12CZnXAmItVwru7ak4",
    "order_items_dataset.csv": "1w2Y4OzDo-CUMJdKLFdHvyCPrBBqyCGfe",
    "order_payments_dataset.csv": "13fdkrfpBCsLEtPBTgDB3yMzhaBIdj2OX",
    "order_reviews_dataset.csv": "14iUX-PgN_tGpye91vQYwrA5BAjtjmz-D",
    "products_dataset.csv": "1eIWew5YsgVb-dvV38zf_RYuj7TWZOVAr"
}

for file_name, file_id in file_ids.items():
    download_url = f"https://drive.google.com/uc?id={file_id}"
    output_file = os.path.join(output_dir, file_name)
    if not os.path.exists(output_file):
        gdown.download(download_url, output_file, quiet=False)

# Load datasets
try:
    sellers_df = pd.read_csv(os.path.join(output_dir, "sellers_dataset.csv"))
    customers_df = pd.read_csv(os.path.join(output_dir, "customers_dataset.csv"))
    orders_df = pd.read_csv(os.path.join(output_dir, "orders_dataset.csv"))
    order_items_df = pd.read_csv(os.path.join(output_dir, "order_items_dataset.csv"))


except Exception as e:
    st.error(f"Error loading datasets: {e}")
    st.stop()

orders_df = orders_df.dropna(subset=["order_approved_at", "order_delivered_customer_date"])
orders_df["order_approved_at"] = pd.to_datetime(orders_df["order_approved_at"])

merged_df = pd.merge(orders_df, order_items_df, on="order_id", how="inner")
merged_df = pd.merge(merged_df, customers_df, on="customer_id", how="inner")

merged_df['year_month'] = merged_df['order_approved_at'].dt.to_period('M').astype(str)
merged_df['price'] = pd.to_numeric(merged_df['price'], errors='coerce')

sales_by_month = (
    merged_df.groupby('year_month')['price']
    .sum()
    .reset_index()
    .rename(columns={'price': 'total_spending'})
)



customer_spending = (
    merged_df.groupby("customer_id")["price"]
    .sum()
    .reset_index()
    .rename(columns={"price": "total_spending"})
)

data_0_600 = customer_spending[customer_spending["total_spending"] <= 600]
data_600_13440 = customer_spending[
    (customer_spending["total_spending"] > 600) & (customer_spending["total_spending"] <= 13440)
]

st.sidebar.header("Visualizations")
show_histogram = st.sidebar.checkbox(" Pertanyaan 1 ")
show_state_spending = st.sidebar.checkbox("Pertanyaan 2")
show_interactive_chart = st.sidebar.checkbox("Sales by Month Chart - interaktif")


if show_histogram:
    st.markdown("""
                **Bagaimana sebaran pembelian pelanggan dan bagaimana pelanggan dapat dikelompokkan berdasarkan jumlah pengeluarannya?**

                Dari data yang telah diolah, sebaran pembelian dikelomppokkan menjadi 'high spender' dan 'low spender'.
                High spender didefinisikan sebagai pembeli yang mengeluarkan uang lebih dari 600 BRL, sedangkan 'low spender'
                didefiniskan sebagai pelanggan yang mengeluarkan uang kurang dari 600 BRL. 

                Informasi lebih jelas ditunjukkan oleh dua histogram berikut.
                """)
    st.markdown("**Spending Histogram for 'low spender'**")
    bins_0_600 = range(0, 601, 100)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data_0_600["total_spending"], bins=bins_0_600, color="skyblue", edgecolor="black")
    ax.set_title("Histogram of Total Spending (0-600)", fontsize=16)
    ax.set_xlabel("Spending Range", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_xticks(bins_0_600)
    st.pyplot(fig)
    

    st.markdown("**Spending Histogram for 'high spender'**")
    bins_600_13440 = range(600, 13441, 100)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data_600_13440["total_spending"], bins=bins_600_13440, color="gray", edgecolor="black")
    ax.set_title("Histogram of Total Spending (600-13440)", fontsize=16)
    ax.set_xlabel("Spending Range", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    xtick_positions = range(600, 13500, 1000)
    ax.set_xticks(xtick_positions)
    ax.set_xticklabels(xtick_positions, rotation=45)
    st.pyplot(fig)

    st.markdown("""Pie chart berikut membandingkan seberapa besar pengeluaran total yang berasal dari masing-masing kelompok.""")
    
    st.subheader("Spending Pie Chart")
    st.text("This pie chart divides spending into high and low spenders for better understanding.")
    low_spending = merged_df[merged_df["price"] <= 600]["price"].sum()
    high_spending = merged_df[(merged_df["price"] > 600) & (merged_df["price"] <= 13440)]["price"].sum()
    labels = ["Low Spending", "High Spending"]
    sizes = [low_spending, high_spending]
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=["skyblue", "orange"])
    ax.set_title("Spending Distribution")
    st.pyplot(fig)

    st.markdown("""Apa yang bisa didapatkan dari kedua pengelompokan ini? 
                Pengelola e-commerce bisa melakukan teknik marketing yang cocok untuk masing-masing kelompok. 
                Kelompok low spender memiliki populasi besar, namun masing-masing pelanggan hanya menghabiskan
                uang dalam jumlah kecil di e-commerce.
                Sebaliknya, kelompok high spender memiliki populasi yang kecil namun dengan pengeluaran tiap
                pelanggan yang jauh lebih besar. 
                Pengelola e-commerce dapat melakukan upaya yang berbeda untuk mengenjaga loyalitas dan meningkatkan
                penjualan dari masing-masing kelompok
""")

if show_state_spending:
    st.markdown("""**Di negara bagian mana penjualan memiliki potensi yang menjanjikan dan pantas untuk diperhatikan?**
                Dari data yang telah diolah, transaksi-transaksi dirangkum dalam satuan mata uang. Kemudian jumlah transaksi dikelompokkan berdasarkan 
                negara bagian asal pembeli. """)
    st.markdown("**This visualization highlights which states have the highest spending.**")
    state_spending = merged_df.groupby("customer_state")["price"].sum().reset_index()
    

    state_spending.columns = ["State", "Total Spending (BRL)"]
    
    state_spending = state_spending.sort_values(by="Total Spending (BRL)", ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.bar(state_spending["State"], state_spending["Total Spending (BRL)"], color="skyblue")
    ax.set_title("Total Spending by State", fontsize=16)
    ax.set_xlabel("State", fontsize=12)
    ax.set_ylabel("Total Spending (BRL)", fontsize=12)
    st.pyplot(fig)

    st.markdown("Untuk visualisasi yang lebih baik, berikut pie chart yang menghimpun informasi dari bar chart di atas.")
    
    top_7_states = state_spending.head(7)
    other_states_spending = state_spending.iloc[7:]["Total Spending (BRL)"].sum()

    labels = list(top_7_states["State"]) + ["Other States"]
    spending_values = list(top_7_states["Total Spending (BRL)"]) + [other_states_spending]

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        spending_values,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=plt.cm.tab10.colors[:len(labels)]
    )
    ax.set_title('Spending Distribution by State (Top 7 + Others)', fontsize=14)
    st.pyplot(fig)
    

    st.markdown("""- Dari bar chart yang telah ditampilkan, dapat dilihat buying power yang didefinisakan sebagai seberapa banyak pemasukan dari pelanggan yang berasal dari negara bagian tersebut. State SP memiliki buying power terbesar dnegan volume BRL >5.000.000, diikuti RJ, MG, RS, dan negara bagian lain.
- Dari pie chart yang telah ditampilkan, terlihat bahwa buying power negara bagian SP mencaplok proporsi 38,3 persen dari total buying power. Negara bagian RJ mengikuti  dengan buying power 13.3 persen an MG dengan 11.7%.""")

if show_interactive_chart:
    st.subheader("Interactive Sales by Month Chart")
    min_month = 0
    max_month = len(sales_by_month) - 1
    start_month, end_month = st.slider(
        "Select the range of months",
        min_value=min_month,
        max_value=max_month,
        value=(min_month, max_month),
        format="%d"
    )

    filtered_sales = sales_by_month.iloc[start_month:end_month]

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=filtered_sales, x='year_month', y='total_spending', marker='o', color='b', ax=ax)

    z = np.polyfit(range(len(filtered_sales)), filtered_sales['total_spending'], 1)
    p = np.poly1d(z)
    ax.plot(filtered_sales['year_month'], p(range(len(filtered_sales))), "r--")

    ax.set_title('Total Sales by Month (Interactive)', fontsize=16)
    ax.set_xlabel('Year-Month', fontsize=12)
    ax.set_ylabel('Total Sales', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("""- Analisis lanjutan dari pertanyaan pertama dilakukan. Dari dua kelompok yang sudah dijelaskan sebelumnya, ingin diketahui juga pembelian yang terjadi secara time series. Analisis ini dilakukan untuk melihat bagaimana performa penjuala e-commerce sepanjang waktu.
    - Digunakan line chart seperti yang ditampilkan di atas. Pada line chart tersebut, digunakan periode waktu selama satu bulan. Ditemukan bahwa penjualan dimulai pada bulan september 2016 dengan keadaan penjualan 0, dan meningkat sepanjang waktu.
    - Digunakan juga trend line untuk melihat bagaimana performa penjualan secara umum. Trend line menunjukkan tren naik, yang artinya penjualan terus meningkat sepanjang waktu dan secara umum dapat dibilang baik.
    - Side bar bisa digunakan jika pengguna ingin melihat garis tren pada periode yang lebih spesifik""")
