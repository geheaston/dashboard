import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="1. Curah Hujan",
    page_icon="🌧️",
    layout="wide"
)

st.title("🌧️ Analisis Curah Hujan (CH)")

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

# ============================================================================
# FILTER DATA DI SIDEBAR
# ============================================================================
st.sidebar.markdown("### 🔍 Filter Data")

# Validasi kolom CH
if 'CH' not in df.columns:
    st.error("❌ Kolom 'CH' tidak ditemukan dalam data")
    st.stop()

# Dapatkan range nilai CH
ch_min = float(df['CH'].min())
ch_max = float(df['CH'].max())

# Slider filter
ch_range = st.sidebar.slider(
    "📊 Rentang Curah Hujan (CH):",
    min_value=ch_min,
    max_value=ch_max,
    value=(ch_min, ch_max),
    step=0.1,
    help="Pilih rentang nilai curah hujan untuk dianalisis"
)

# Filter dataframe
df_filtered = df[(df['CH'] >= ch_range[0]) & (df['CH'] <= ch_range[1])].copy()

# ============================================================================
# VALIDASI DATA UNTUK PETA
# ============================================================================
df_map = df_filtered.dropna(subset=['LON', 'LAT', 'CH']).copy()

if len(df_map) == 0:
    st.warning("⚠️ Tidak ada data yang tersedia untuk range yang dipilih. Silakan sesuaikan filter.")
    st.stop()

# ============================================================================
# ROW 1: KPI METRICS
# ============================================================================
st.markdown("### 📈 Ringkasan Statistik")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Titik Grid",
        value=len(df_map),
        help="Jumlah grid dengan data curah hujan"
    )

with col2:
    avg_ch = df_map['CH'].mean()
    st.metric(
        label="Rata-rata Curah Hujan",
        value=f"{avg_ch:.2f}",
        help="Rata-rata nilai CH dalam filter"
    )

with col3:
    max_ch = df_map['CH'].max()
    st.metric(
        label="Curah Hujan Maksimum",
        value=f"{max_ch:.2f}",
        help="Nilai curah hujan tertinggi dalam filter"
    )

st.markdown("---")

# ============================================================================
# ROW 2: PETA INTERAKTIF SCATTER MAPBOX
# ============================================================================
st.markdown("### 🗺️ Peta Sebaran Spasial Curah Hujan")

try:
    fig_map = px.scatter_mapbox(
        df_map,
        lat='LAT',
        lon='LON',
        color='CH',
        hover_name=None,
        hover_data={
            'LAT': ':.4f',
            'LON': ':.4f',
            'CH': ':.2f'
        },
        color_continuous_scale='YlOrRd',
        zoom=3,
        center=dict(lat=df_map['LAT'].mean(), lon=df_map['LON'].mean()),
        mapbox_style='carto-positron',
        title='Distribusi Spasial Curah Hujan di Grid',
        labels={
            'CH': 'Curah Hujan (mm)',
            'LAT': 'Latitude',
            'LON': 'Longitude'
        }
    )
    
    fig_map.update_layout(
        height=500,
        hovermode='closest'
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
except Exception as e:
    st.error(f"❌ Error membuat peta: {e}")

st.markdown("---")

# ============================================================================
# ROW 3: HISTOGRAM DISTRIBUSI
# ============================================================================
st.markdown("### 📊 Distribusi Frekuensi Curah Hujan")

col_hist1, col_hist2 = st.columns([2, 1])

with col_hist1:
    try:
        fig_hist = px.histogram(
            df_map,
            x='CH',
            nbins=30,
            title='Histogram Distribusi Curah Hujan',
            labels={'CH': 'Curah Hujan (mm)', 'count': 'Frekuensi'},
            color_discrete_sequence=['#FF9999']
        )
        
        fig_hist.add_vline(
            x=df_map['CH'].mean(),
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {df_map['CH'].mean():.2f}",
            annotation_position="top right"
        )
        
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error membuat histogram: {e}")

with col_hist2:
    st.markdown("#### 📌 Statistik Deskriptif")
    stats = {
        'Min': df_map['CH'].min(),
        'Q1 (25%)': df_map['CH'].quantile(0.25),
        'Median': df_map['CH'].median(),
        'Mean': df_map['CH'].mean(),
        'Q3 (75%)': df_map['CH'].quantile(0.75),
        'Max': df_map['CH'].max(),
        'Std Dev': df_map['CH'].std()
    }
    
    for stat_name, stat_value in stats.items():
        st.write(f"**{stat_name}:** `{stat_value:.4f}`")

st.markdown("---")

# ============================================================================
# ROW 4: DATAFRAME TABEL
# ============================================================================
st.markdown("### 📋 Data Hasil Filter")

# Persiapan dataframe untuk display
df_display = df_map[['LON', 'LAT', 'CH']].copy()
df_display = df_display.round(4)

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

# Opsi download data
st.markdown("#### 💾 Unduh Data")
csv = df_display.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="curah_hujan_analysis.csv",
    mime="text/csv",
    help="Unduh data hasil filter dalam format CSV"
)

st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 12px; color: #888;'>
    Halaman Analisis Curah Hujan | Data berbasis GRID spasial dari satelit
</div>
""", unsafe_allow_html=True)
