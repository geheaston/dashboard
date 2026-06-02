import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="2. Sifat Hujan",
    page_icon="💧",
    layout="wide"
)

st.title("💧 Analisis Sifat Hujan (SH%)")

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
        numeric_cols = ['LON', 'LAT', 'SH%', 'SHpercent']
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
# DETEKSI KOLOM SIFAT HUJAN
# ============================================================================
sh_col = None
if 'SH%' in df.columns and df['SH%'].notna().sum() > 0:
    sh_col = 'SH%'
elif 'SHpercent' in df.columns and df['SHpercent'].notna().sum() > 0:
    sh_col = 'SHpercent'

if sh_col is None:
    st.error("❌ Kolom 'SH%' atau 'SHpercent' tidak ditemukan dalam data")
    st.stop()

# ============================================================================
# FILTER DATA DI SIDEBAR
# ============================================================================
st.sidebar.markdown("### 🔍 Filter Data")

# Dapatkan range nilai SH%
sh_min = float(df[sh_col].min())
sh_max = float(df[sh_col].max())

# Slider filter
sh_range = st.sidebar.slider(
    f"📊 Rentang Sifat Hujan ({sh_col}):",
    min_value=sh_min,
    max_value=sh_max,
    value=(sh_min, sh_max),
    step=0.1,
    help="Pilih rentang nilai sifat hujan untuk dianalisis"
)

# Filter dataframe
df_filtered = df[(df[sh_col] >= sh_range[0]) & (df[sh_col] <= sh_range[1])].copy()

# ============================================================================
# VALIDASI DATA UNTUK PETA
# ============================================================================
df_map = df_filtered.dropna(subset=['LON', 'LAT', sh_col]).copy()

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
        help="Jumlah grid dengan data sifat hujan"
    )

with col2:
    avg_sh = df_map[sh_col].mean()
    st.metric(
        label="Rata-rata Sifat Hujan",
        value=f"{avg_sh:.2f}%",
        help="Rata-rata nilai sifat hujan dalam filter"
    )

with col3:
    max_sh = df_map[sh_col].max()
    st.metric(
        label="Sifat Hujan Tertinggi",
        value=f"{max_sh:.2f}%",
        help="Nilai sifat hujan tertinggi dalam filter"
    )

st.markdown("---")

# ============================================================================
# ROW 2: PETA INTERAKTIF SCATTER MAPBOX DENGAN SKALA WARNA DIVERGEN
# ============================================================================
st.markdown("### 🗺️ Peta Sebaran Spasial Sifat Hujan")

try:
    fig_map = px.scatter_mapbox(
        df_map,
        lat='LAT',
        lon='LON',
        color=sh_col,
        hover_name=None,
        hover_data={
            'LAT': ':.4f',
            'LON': ':.4f',
            sh_col: ':.2f'
        },
        color_continuous_scale='RdYlGn',  # Merah-Kuning-Hijau (divergen)
        zoom=3,
        center=dict(lat=df_map['LAT'].mean(), lon=df_map['LON'].mean()),
        mapbox_style='carto-positron',
        title='Distribusi Spasial Sifat Hujan di Grid',
        labels={
            sh_col: 'Sifat Hujan (%)',
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
# ROW 3: PIE/DONUT CHART DENGAN KATEGORI
# ============================================================================
st.markdown("### 📊 Klasifikasi Sifat Hujan")

# Kategori sifat hujan
def kategorisasi_sh(value):
    if value < 85:
        return 'Bawah Normal'
    elif value <= 115:
        return 'Normal'
    else:
        return 'Atas Normal'

df_map['Kategori'] = df_map[sh_col].apply(kategorisasi_sh)
kategori_counts = df_map['Kategori'].value_counts()

col_pie1, col_pie2 = st.columns([2, 1])

with col_pie1:
    try:
        # Define colors for categories
        color_map = {
            'Bawah Normal': '#FF6B6B',  # Red
            'Normal': '#4ECDC4',        # Teal
            'Atas Normal': '#95E77D'    # Green
        }
        
        colors = [color_map.get(cat, '#888') for cat in kategori_counts.index]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=kategori_counts.index,
            values=kategori_counts.values,
            hole=0.3,  # Donut chart
            marker=dict(colors=colors),
            textposition='inside',
            textinfo='label+percent'
        )])
        
        fig_pie.update_layout(
            title='Proporsi Kategori Sifat Hujan',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error membuat pie chart: {e}")

with col_pie2:
    st.markdown("#### 📌 Detail Kategori")
    for kategori, count in kategori_counts.items():
        percentage = (count / len(df_map)) * 100
        st.write(f"**{kategori}**: {count} grid ({percentage:.1f}%)")
    
    st.markdown("#### 📋 Definisi")
    st.markdown("""
    - **Bawah Normal:** SH% < 85%
    - **Normal:** 85% ≤ SH% ≤ 115%
    - **Atas Normal:** SH% > 115%
    """)

st.markdown("---")

# ============================================================================
# ROW 4: HISTOGRAM DISTRIBUSI
# ============================================================================
st.markdown("### 📊 Distribusi Frekuensi Sifat Hujan")

try:
    fig_hist = px.histogram(
        df_map,
        x=sh_col,
        nbins=25,
        title='Histogram Distribusi Sifat Hujan',
        labels={sh_col: 'Sifat Hujan (%)', 'count': 'Frekuensi'},
        color_discrete_sequence=['#4ECDC4']
    )
    
    fig_hist.add_vline(
        x=df_map[sh_col].mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: {df_map[sh_col].mean():.2f}%",
        annotation_position="top right"
    )
    
    fig_hist.update_layout(height=400)
    st.plotly_chart(fig_hist, use_container_width=True)
    
except Exception as e:
    st.error(f"❌ Error membuat histogram: {e}")

st.markdown("---")

# ============================================================================
# ROW 5: DATAFRAME TABEL
# ============================================================================
st.markdown("### 📋 Data Hasil Filter")

# Persiapan dataframe untuk display
df_display = df_map[['LON', 'LAT', sh_col, 'Kategori']].copy()
df_display = df_display.rename(columns={sh_col: 'Sifat Hujan (%)'})
df_display['LON'] = df_display['LON'].round(4)
df_display['LAT'] = df_display['LAT'].round(4)
df_display['Sifat Hujan (%)'] = df_display['Sifat Hujan (%)'].round(2)

st.dataframe(
    df_display,
    use_container_width=True,
    height=400,
    column_config={
        'LON': st.column_config.NumberColumn('Longitude', format='%.4f'),
        'LAT': st.column_config.NumberColumn('Latitude', format='%.4f'),
        'Sifat Hujan (%)': st.column_config.NumberColumn('Sifat Hujan (%)', format='%.2f'),
        'Kategori': st.column_config.TextColumn('Kategori')
    }
)

# Opsi download data
st.markdown("#### 💾 Unduh Data")
csv = df_display.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="sifat_hujan_analysis.csv",
    mime="text/csv",
    help="Unduh data hasil filter dalam format CSV"
)

st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 12px; color: #888;'>
    Halaman Analisis Sifat Hujan | Data berbasis GRID spasial dari satelit
</div>
""", unsafe_allow_html=True)
