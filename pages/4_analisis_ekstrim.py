import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="4. Analisis Ekstrim",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Analisis Ekstrim (Extreme Rainfall & Threshold Analysis)")

# ============================================================================
# FUNGSI LOAD DATA DENGAN CACHE
# ============================================================================
@st.cache_data
def load_data():
    """Load data dari file Excel dengan cache untuk performa optimal"""
    try:
        file_path = "data/BlendGSMAP_POS.202605dec02.xls"
        df = pd.read_excel(file_path, engine='xlrd')
        
        # Strip whitespace dari nama kolom
        df.columns = df.columns.str.strip()
        
        # Strip whitespace dari data text (jika ada)
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        
        # Konversi kolom numerik
        numeric_cols = ['LON', 'LAT', 'CH']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"❌ Error membaca file data: {e}")
        return None

# Load data
df = load_data()

if df is None:
    st.stop()

if 'CH' not in df.columns:
    st.error("❌ Kolom 'CH' tidak ditemukan dalam data")
    st.stop()

# ============================================================================
# FILTER DATA DI SIDEBAR
# ============================================================================
st.sidebar.markdown("### 🔍 Filter Data")

ch_min = float(df['CH'].min())
ch_max = float(df['CH'].max())

# Slider untuk ambang batas ekstrim
threshold = st.sidebar.slider(
    "⚠️ Ambang Batas Curah Hujan Ekstrim (mm):",
    min_value=ch_min,
    max_value=ch_max,
    value=ch_max * 0.75,  # Default 75% dari max
    step=1.0,
    help="Tentukan ambang batas untuk mendeteksi curah hujan ekstrim"
)

# Filter data ekstrim
df_ekstrim = df[df['CH'] >= threshold].dropna(subset=['LON', 'LAT', 'CH']).copy()
df_all_clean = df.dropna(subset=['LON', 'LAT', 'CH']).copy()

if len(df_ekstrim) == 0:
    st.warning("⚠️ Tidak ada data yang melebihi ambang batas ekstrim. Silakan turunkan nilai ambang batas.")
    st.stop()

# ============================================================================
# ROW 1: KPI METRICS
# ============================================================================
st.markdown("### 📊 Ringkasan Deteksi Ekstrim")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Titik Ekstrim",
        value=len(df_ekstrim),
        help="Jumlah grid yang melebihi ambang batas"
    )

with col2:
    pct_ekstrim = (len(df_ekstrim) / len(df_all_clean)) * 100
    st.metric(
        label="Persentase Area Ekstrim",
        value=f"{pct_ekstrim:.2f}%",
        help="Persentase grid terdampak dari total grid"
    )

with col3:
    avg_ekstrim = df_ekstrim['CH'].mean()
    st.metric(
        label="Rata-rata Curah Hujan Ekstrim",
        value=f"{avg_ekstrim:.2f} mm",
        help="Rata-rata nilai CH di area ekstrim"
    )

with col4:
    max_ekstrim = df_ekstrim['CH'].max()
    st.metric(
        label="Curah Hujan Maksimum",
        value=f"{max_ekstrim:.2f} mm",
        help="Nilai curah hujan tertinggi"
    )

st.markdown("---")

# ============================================================================
# ROW 2: PETA SPASIAL EKSTRIM
# ============================================================================
st.markdown("### 🗺️ Peta Lokasi Curah Hujan Ekstrim")

try:
    # Buat dataframe dengan kategori
    df_map = df_all_clean.copy()
    df_map['Kategori'] = df_map['CH'].apply(
        lambda x: 'Ekstrim' if x >= threshold else 'Normal'
    )
    
    # Warna berbeda untuk ekstrim vs normal
    color_map = {'Ekstrim': '#FF0000', 'Normal': '#CCCCCC'}
    
    fig_map = px.scatter_mapbox(
        df_map,
        lat='LAT',
        lon='LON',
        color='Kategori',
        hover_data={
            'LAT': ':.4f',
            'LON': ':.4f',
            'CH': ':.2f',
            'Kategori': True
        },
        color_discrete_map=color_map,
        zoom=3,
        center=dict(lat=df_map['LAT'].mean(), lon=df_map['LON'].mean()),
        mapbox_style='carto-positron',
        title=f'Deteksi Area Ekstrim (CH ≥ {threshold:.1f} mm)',
        labels={
            'CH': 'Curah Hujan (mm)',
            'LAT': 'Latitude',
            'LON': 'Longitude',
            'Kategori': 'Kategori'
        }
    )
    
    # Update marker untuk ekstrim terlihat lebih jelas
    fig_map.update_traces(
        marker=dict(
            size=8,
            opacity=0.8,
            line=dict(width=0)
        )
    )
    
    fig_map.update_layout(
        height=500,
        hovermode='closest'
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.info("""
    **Interpretasi Peta:**
    - 🔴 **Merah:** Area dengan curah hujan ekstrim (melebihi ambang batas)
    - ⚪ **Abu-abu:** Area dengan curah hujan normal (di bawah ambang batas)
    """)
    
except Exception as e:
    st.error(f"❌ Error membuat peta: {e}")

st.markdown("---")

# ============================================================================
# ROW 3: DISTRIBUSI EKSTRIM
# ============================================================================
st.markdown("### 📊 Histogram Curah Hujan Ekstrim")

col_hist1, col_hist2 = st.columns([2, 1])

with col_hist1:
    try:
        fig_hist = px.histogram(
            df_ekstrim,
            x='CH',
            nbins=20,
            title='Distribusi Frekuensi Curah Hujan di Area Ekstrim',
            labels={'CH': 'Curah Hujan (mm)', 'count': 'Frekuensi'},
            color_discrete_sequence=['#FF6B6B']
        )
        
        fig_hist.add_vline(
            x=threshold,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Threshold: {threshold:.1f} mm",
            annotation_position="top right"
        )
        
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error membuat histogram: {e}")

with col_hist2:
    st.markdown("#### 📌 Kategori Ekstrim")
    
    # Definisi kategori hujan
    kategori_defs = {
        'Lebat': (threshold, threshold * 1.5),
        'Sangat Lebat': (threshold * 1.5, df_ekstrim['CH'].max() + 1)
    }
    
    for kat_name, (lower, upper) in kategori_defs.items():
        count = len(df_ekstrim[(df_ekstrim['CH'] >= lower) & (df_ekstrim['CH'] < upper)])
        if count > 0:
            pct = (count / len(df_ekstrim)) * 100
            st.write(f"**{kat_name}:** {count} grid ({pct:.1f}%)")

st.markdown("---")

# ============================================================================
# ROW 4: TABEL TOP 10 EKSTRIM
# ============================================================================
st.markdown("### 📋 Top 10 Lokasi Ekstrim (Mitigasi Prioritas)")

# Sort dan ambil top 10
df_top10 = df_ekstrim.nlargest(10, 'CH')[['LON', 'LAT', 'CH']].copy()
df_top10['Rank'] = range(1, len(df_top10) + 1)
df_top10 = df_top10[['Rank', 'LON', 'LAT', 'CH']]
df_top10['LON'] = df_top10['LON'].round(4)
df_top10['LAT'] = df_top10['LAT'].round(4)
df_top10['CH'] = df_top10['CH'].round(2)

st.dataframe(
    df_top10,
    use_container_width=True,
    column_config={
        'Rank': st.column_config.NumberColumn('Ranking', format='%d'),
        'LON': st.column_config.NumberColumn('Longitude', format='%.4f'),
        'LAT': st.column_config.NumberColumn('Latitude', format='%.4f'),
        'CH': st.column_config.NumberColumn('Curah Hujan (mm)', format='%.2f')
    }
)

st.markdown("#### 💾 Unduh Data")
csv = df_top10.to_csv(index=False)
st.download_button(
    label="Download CSV - Top 10 Ekstrim",
    data=csv,
    file_name="top10_ekstrim.csv",
    mime="text/csv",
    help="Unduh daftar 10 lokasi dengan curah hujan ekstrim tertinggi"
)

st.markdown("---")

# ============================================================================
# ROW 5: SEMUA DATA EKSTRIM
# ============================================================================
st.markdown("### 📋 Semua Data Curah Hujan Ekstrim")

df_display = df_ekstrim[['LON', 'LAT', 'CH']].copy()
df_display['LON'] = df_display['LON'].round(4)
df_display['LAT'] = df_display['LAT'].round(4)
df_display['CH'] = df_display['CH'].round(2)

st.dataframe(
    df_display,
    use_container_width=True,
    height=400,
    column_config={
        'LON': st.column_config.NumberColumn('Longitude', format='%.4f'),
        'LAT': st.column_config.NumberColumn('Latitude', format='%.4f'),
        'CH': st.column_config.NumberColumn('Curah Hujan (mm)', format='%.2f')
    }
)

# Download semua data ekstrim
csv_all = df_display.to_csv(index=False)
st.download_button(
    label="Download CSV - Semua Data Ekstrim",
    data=csv_all,
    file_name="semua_data_ekstrim.csv",
    mime="text/csv",
    help="Unduh semua grid dengan curah hujan ekstrim"
)

st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 12px; color: #888;'>
    Halaman Analisis Ekstrim | Deteksi Curah Hujan Ekstrim untuk Mitigasi Bencana
</div>
""", unsafe_allow_html=True)
