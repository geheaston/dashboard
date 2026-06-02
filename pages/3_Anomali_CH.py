import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="3. Anomali Curah Hujan",
    page_icon="📍",
    layout="wide"
)

st.title("📍 Analisis Anomali Curah Hujan (AnomCH)")

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
        numeric_cols = ['LON', 'LAT', 'AnomCH']
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
# VALIDASI KOLOM ANOMALI
# ============================================================================
if 'AnomCH' not in df.columns:
    st.error("❌ Kolom 'AnomCH' tidak ditemukan dalam data")
    st.stop()

# ============================================================================
# FILTER DATA DI SIDEBAR
# ============================================================================
st.sidebar.markdown("### 🔍 Filter Data")

# Dapatkan range nilai AnomCH
anom_min = float(df['AnomCH'].min())
anom_max = float(df['AnomCH'].max())

# Slider filter
anom_range = st.sidebar.slider(
    "📊 Rentang Anomali Curah Hujan (AnomCH):",
    min_value=anom_min,
    max_value=anom_max,
    value=(anom_min, anom_max),
    step=0.1,
    help="Pilih rentang nilai anomali untuk dianalisis (negatif = di bawah normal, positif = di atas normal)"
)

# Filter dataframe
df_filtered = df[(df['AnomCH'] >= anom_range[0]) & (df['AnomCH'] <= anom_range[1])].copy()

# ============================================================================
# VALIDASI DATA UNTUK PETA
# ============================================================================
df_map = df_filtered.dropna(subset=['LON', 'LAT', 'AnomCH']).copy()

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
        help="Jumlah grid dengan data anomali"
    )

with col2:
    avg_anom = df_map['AnomCH'].mean()
    st.metric(
        label="Rata-rata Anomali",
        value=f"{avg_anom:.2f}",
        help="Rata-rata nilai anomali dalam filter"
    )

with col3:
    # Tampilkan min dan max anomali
    min_anom = df_map['AnomCH'].min()
    max_anom = df_map['AnomCH'].max()
    extreme_anom = min_anom if abs(min_anom) > abs(max_anom) else max_anom
    
    st.metric(
        label="Anomali Ekstrem",
        value=f"{extreme_anom:.2f}",
        help="Nilai anomali paling ekstrem (paling negatif atau paling positif)"
    )

st.markdown("---")

# ============================================================================
# ROW 2: PETA INTERAKTIF SCATTER MAPBOX DENGAN SKALA WARNA DIVERGEN
# ============================================================================
st.markdown("### 🗺️ Peta Sebaran Spasial Anomali Curah Hujan")

try:
    # Tentukan center value untuk scale warna divergen
    anom_abs_max = max(abs(df_map['AnomCH'].min()), abs(df_map['AnomCH'].max()))
    
    fig_map = px.scatter_mapbox(
        df_map,
        lat='LAT',
        lon='LON',
        color='AnomCH',
        hover_name=None,
        hover_data={
            'LAT': ':.4f',
            'LON': ':.4f',
            'AnomCH': ':.2f'
        },
        color_continuous_scale='RdBu_r',  # Merah-Biru (divergen, reversed)
        color_continuous_midpoint=0,  # Tengah di 0
        zoom=3,
        center=dict(lat=df_map['LAT'].mean(), lon=df_map['LON'].mean()),
        mapbox_style='carto-positron',
        title='Distribusi Spasial Anomali Curah Hujan di Grid',
        labels={
            'AnomCH': 'Anomali CH',
            'LAT': 'Latitude',
            'LON': 'Longitude'
        }
    )
    
    # Customize colorbar
    fig_map.update_coloraxes(
        colorbar=dict(
            title="Anomali<br>(mm)",
            tickmode="linear"
        )
    )
    
    fig_map.update_layout(
        height=500,
        hovermode='closest'
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.info("""
    **Interpretasi Warna:**
    - 🔴 **Merah:** Anomali POSITIF (curah hujan lebih tinggi dari normal)
    - ⚪ **Putih/Netral:** Anomali mendekati NOLBATCH (curah hujan normal)
    - 🔵 **Biru:** Anomali NEGATIF (curah hujan lebih rendah dari normal)
    """)
    
except Exception as e:
    st.error(f"❌ Error membuat peta: {e}")

st.markdown("---")

# ============================================================================
# ROW 3: BAR CHART / HISTOGRAM ANOMALI POSITIF VS NEGATIF
# ============================================================================
st.markdown("### 📊 Distribusi Anomali (Positif vs Negatif)")

# Kategorisasi anomali
df_map['Tipe_Anomali'] = df_map['AnomCH'].apply(
    lambda x: 'Positif (Lebih Hujan)' if x > 0 else ('Negatif (Kurang Hujan)' if x < 0 else 'Normal')
)

col_dist1, col_dist2 = st.columns([2, 1])

with col_dist1:
    try:
        # Bar chart perbandingan
        anom_type_counts = df_map['Tipe_Anomali'].value_counts()
        
        fig_bar = go.Figure(data=[
            go.Bar(
                x=anom_type_counts.index,
                y=anom_type_counts.values,
                marker=dict(
                    color=['#FF6B6B', '#4ECDC4', '#95E77D'],
                    line=dict(color='#222', width=1)
                ),
                text=anom_type_counts.values,
                textposition='outside'
            )
        ])
        
        fig_bar.update_layout(
            title='Jumlah Grid berdasarkan Tipe Anomali',
            xaxis_title='Tipe Anomali',
            yaxis_title='Jumlah Grid',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error membuat bar chart: {e}")

with col_dist2:
    st.markdown("#### 📌 Ringkasan Tipe Anomali")
    
    anom_type_counts = df_map['Tipe_Anomali'].value_counts()
    for tipe, count in anom_type_counts.items():
        percentage = (count / len(df_map)) * 100
        st.write(f"**{tipe}**: {count} grid ({percentage:.1f}%)")

st.markdown("---")

# ============================================================================
# ROW 4: HISTOGRAM DISTRIBUSI ANOMALI DETAIL
# ============================================================================
st.markdown("### 📊 Distribusi Frekuensi Anomali Curah Hujan")

try:
    fig_hist = px.histogram(
        df_map,
        x='AnomCH',
        nbins=30,
        title='Histogram Distribusi Anomali Curah Hujan',
        labels={'AnomCH': 'Anomali Curah Hujan (mm)', 'count': 'Frekuensi'},
        color_discrete_sequence=['#9B59B6']
    )
    
    # Tambahkan garis vertical di 0
    fig_hist.add_vline(
        x=0,
        line_dash="dash",
        line_color="black",
        annotation_text="Normal (Anomali=0)",
        annotation_position="top center"
    )
    
    # Tambahkan garis mean
    fig_hist.add_vline(
        x=df_map['AnomCH'].mean(),
        line_dash="dot",
        line_color="green",
        annotation_text=f"Mean: {df_map['AnomCH'].mean():.2f}",
        annotation_position="top right"
    )
    
    fig_hist.update_layout(height=400)
    st.plotly_chart(fig_hist, use_container_width=True)
    
except Exception as e:
    st.error(f"❌ Error membuat histogram: {e}")

st.markdown("---")

# ============================================================================
# ROW 5: STATISTIK DESKRIPTIF
# ============================================================================
st.markdown("### 📋 Statistik Deskriptif Anomali")

stats_col1, stats_col2, stats_col3 = st.columns(3)

with stats_col1:
    st.markdown("#### Anomali Positif (Lebih Hujan)")
    anom_pos = df_map[df_map['AnomCH'] > 0]['AnomCH']
    if len(anom_pos) > 0:
        st.write(f"**Jumlah Grid:** {len(anom_pos)}")
        st.write(f"**Rata-rata:** {anom_pos.mean():.2f}")
        st.write(f"**Maksimum:** {anom_pos.max():.2f}")
    else:
        st.write("Tidak ada anomali positif")

with stats_col2:
    st.markdown("#### Anomali Negatif (Kurang Hujan)")
    anom_neg = df_map[df_map['AnomCH'] < 0]['AnomCH']
    if len(anom_neg) > 0:
        st.write(f"**Jumlah Grid:** {len(anom_neg)}")
        st.write(f"**Rata-rata:** {anom_neg.mean():.2f}")
        st.write(f"**Minimum:** {anom_neg.min():.2f}")
    else:
        st.write("Tidak ada anomali negatif")

with stats_col3:
    st.markdown("#### Statistik Keseluruhan")
    st.write(f"**Min:** {df_map['AnomCH'].min():.2f}")
    st.write(f"**Median:** {df_map['AnomCH'].median():.2f}")
    st.write(f"**Mean:** {df_map['AnomCH'].mean():.2f}")
    st.write(f"**Std Dev:** {df_map['AnomCH'].std():.2f}")
    st.write(f"**Max:** {df_map['AnomCH'].max():.2f}")

st.markdown("---")

# ============================================================================
# ROW 6: DATAFRAME TABEL
# ============================================================================
st.markdown("### 📋 Data Hasil Filter")

# Persiapan dataframe untuk display
df_display = df_map[['LON', 'LAT', 'AnomCH', 'Tipe_Anomali']].copy()
df_display = df_display.rename(columns={'AnomCH': 'Anomali (mm)', 'Tipe_Anomali': 'Tipe'})
df_display['LON'] = df_display['LON'].round(4)
df_display['LAT'] = df_display['LAT'].round(4)
df_display['Anomali (mm)'] = df_display['Anomali (mm)'].round(2)

st.dataframe(
    df_display,
    use_container_width=True,
    height=400,
    column_config={
        'LON': st.column_config.NumberColumn('Longitude', format='%.4f'),
        'LAT': st.column_config.NumberColumn('Latitude', format='%.4f'),
        'Anomali (mm)': st.column_config.NumberColumn('Anomali (mm)', format='%.2f'),
        'Tipe': st.column_config.TextColumn('Tipe Anomali')
    }
)

# Opsi download data
st.markdown("#### 💾 Unduh Data")
csv = df_display.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="anomali_curah_hujan_analysis.csv",
    mime="text/csv",
    help="Unduh data hasil filter dalam format CSV"
)

st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 12px; color: #888;'>
    Halaman Analisis Anomali Curah Hujan | Data berbasis GRID spasial dari satelit
</div>
""", unsafe_allow_html=True)
