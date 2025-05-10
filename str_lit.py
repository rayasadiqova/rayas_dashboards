import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="House Listings Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("house_listings.csv")
    df['price'] = df['price'].str.replace(" ", "").str.replace("AZN", "").astype(float)
    df['area_m2'] = df['area'].str.replace(" m²", "").astype(float)
    df['price_1m2'] = df['price_1m2'].str.extract(r'(\d+)').astype(float)
    df['room_number'] = df['room_number'].fillna(0).astype(int)
    return df

df = load_data()

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Descriptives", "Sales", "Profit"])

# Dataset download in sidebar
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 Dataseti CSV formatında yüklə",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name='house_listings.csv',
    mime='text/csv'
)

# Main content
if page == "Descriptives":
    st.title("Tikili növünə görə ümumi baxış")
    st.subheader("Orta qiymət və say")

    avg_price = df.groupby('category')['price'].mean().reset_index()
    count_by_cat = df['category'].value_counts().reset_index()
    count_by_cat.columns = ['category', 'count']

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(avg_price, x='category', y='price', title="Orta qiymət", color='category')
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(count_by_cat, x='category', y='count', title="Elan sayı", color='category')
        st.plotly_chart(fig2, use_container_width=True)

elif page == "Sales":
    st.title("Otaq sayına görə 1 m² qiymət analizi")
    avg_price_room = df.groupby('room_number')['price_1m2'].mean().reset_index()
    fig = px.bar(
        avg_price_room,
        x='room_number',
        y='price_1m2',
        title="Otaq sayına görə orta 1 m² qiymət",
        labels={'room_number': 'Otaq sayı', 'price_1m2': '1 m² qiymət'},
        color='price_1m2'
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "Profit":
    st.title("Rayonlara görə orta qiymət")

    df['rayon'] = df['address'].str.extract(r',\s*([^,]+?)(?:\s+m\.)?$')
    avg_price_rayon = df.groupby('rayon')['price'].mean().reset_index().dropna()

    fig = px.bar(
        avg_price_rayon.sort_values('price', ascending=False),
        x='rayon',
        y='price',
        title="Rayonlara görə orta satış qiyməti",
        labels={'rayon': 'Rayon', 'price': 'Orta qiymət (AZN)'},
        color='price'
    )
    st.plotly_chart(fig, use_container_width=True)

# 🔽 Dataseti yükləmək üçün seçim hissəsi
st.markdown("---")
st.subheader("📁 Verilənləri yüklə")

file_format = st.selectbox(
    "Verilənləri hansı formatda yükləmək istəyirsiniz?",
    ("CSV", "Excel", "Hər ikisi")
)

if file_format == "CSV":
    st.download_button(
        label="📥 CSV formatında yüklə",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='house_listings.csv',
        mime='text/csv'
    )

elif file_format == "Excel":
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
        writer.save()
        st.download_button(
            label="📥 Excel (XLSX) formatında yüklə",
            data=buffer.getvalue(),
            file_name="house_listings.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif file_format == "Hər ikisi":
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📥 CSV yüklə",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='house_listings.csv',
            mime='text/csv'
        )
    with col2:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
            writer.save()
            st.download_button(
                label="📥 Excel yüklə",
                data=buffer.getvalue(),
                file_name="house_listings.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )